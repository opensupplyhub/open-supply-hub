from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from django.utils import timezone

from api.models.extended_field import ExtendedField
from api.models.transactions.index_facilities_new import index_facilities_new


class Command(BaseCommand):
    """
    One-off data fix for OSDEV-2949.

    The 'rsc_grievance_mechanism' partner field was ingested from a
    partner's list contribution that carried an 'internal_ID' nested
    inside each value's 'raw_values'. That key is NOT part of the partner
    field's JSON Schema, and the partner explicitly asked us not to expose
    it, yet it was being returned by the API. This command removes the
    nested 'internal_ID' from every affected ExtendedField so the data
    looks as if the key was never contributed.
    """

    FIELD_NAME = 'rsc_grievance_mechanism'
    RAW_VALUES_KEY = 'raw_values'
    INTERNAL_ID_KEY = 'internal_ID'

    help = (
        "Remove the nested '{key}' key from '{field}' partner field values "
        "(ExtendedField.value['{raw}']['{key}']) and reindex the affected "
        "production locations so the key is no longer returned by "
        "GET /api/facilities and GET /api/v1/production-locations."
    ).format(
        key=INTERNAL_ID_KEY,
        field=FIELD_NAME,
        raw=RAW_VALUES_KEY,
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of rows updated per bulk_update batch (default: 500)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Report what would change without writing to the database.'
        )
        parser.add_argument(
            '--no-reindex',
            action='store_false',
            dest='reindex',
            default=True,
            help=(
                'Skip reindexing the affected locations (the heaviest step). '
                'The ExtendedField rows are still cleaned, but the API keeps '
                'serving the stale index until a reindex runs.'
            )
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        reindex = options['reindex']

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY-RUN enabled: no database writes will be performed.'
            ))

        base_qs = (
            ExtendedField.objects
            .filter(field_name=self.FIELD_NAME)
            .filter(**{
                f'value__{self.RAW_VALUES_KEY}__has_key': self.INTERNAL_ID_KEY
            })
            .order_by('id')
        )

        total = base_qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                f"No '{self.FIELD_NAME}' records contain a nested "
                f"'{self.INTERNAL_ID_KEY}'; nothing to do."
            ))
            return

        self.stdout.write(
            f"Found {total} '{self.FIELD_NAME}' record(s) with a nested "
            f"'{self.INTERNAL_ID_KEY}'."
        )

        stats = {
            'scanned': 0,
            'updated': 0,
            'would_update': 0,
            'skipped': 0,
        }
        affected_facility_ids = set()
        to_update = []

        def flush_batch():
            if not to_update:
                return
            if dry_run:
                stats['would_update'] += len(to_update)
                to_update.clear()
                return
            try:
                with transaction.atomic():
                    ExtendedField.objects.bulk_update(
                        to_update, ['value'], batch_size=batch_size
                    )
                stats['updated'] += len(to_update)
            except DatabaseError as exc:
                self.stderr.write(self.style.ERROR(
                    f'Bulk update failed for batch of {len(to_update)}: {exc}'
                ))
                raise
            finally:
                to_update.clear()

        last_log = timezone.now()
        for extended_field in base_qs.iterator(chunk_size=batch_size):
            stats['scanned'] += 1

            value = extended_field.value
            raw_values = (
                value.get(self.RAW_VALUES_KEY)
                if isinstance(value, dict) else None
            )

            # The queryset guarantees the key exists, but stay defensive
            # against unexpected value shapes so one bad row cannot abort
            # the whole cleanup.
            if (
                not isinstance(raw_values, dict)
                or self.INTERNAL_ID_KEY not in raw_values
            ):
                stats['skipped'] += 1
                continue

            raw_values.pop(self.INTERNAL_ID_KEY)
            extended_field.value = value
            to_update.append(extended_field)

            if extended_field.facility_id is not None:
                affected_facility_ids.add(extended_field.facility_id)

            if len(to_update) >= batch_size:
                flush_batch()

            now = timezone.now()
            if (now - last_log).total_seconds() >= 10:
                self.stdout.write(
                    f"Progress: scanned={stats['scanned']}/{total} "
                    f"updated={stats['updated']} "
                    f"would_update={stats['would_update']} "
                    f"skipped={stats['skipped']}"
                )
                last_log = now

        flush_batch()

        self._reindex(affected_facility_ids, dry_run, reindex)

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            f"Done{' [DRY-RUN]' if dry_run else ''}. "
            f"scanned={stats['scanned']} "
            f"updated={stats['updated']} "
            f"would_update={stats['would_update']} "
            f"skipped={stats['skipped']} "
            f"affected_locations={len(affected_facility_ids)}"
        ))

    def _reindex(self, facility_ids, dry_run, reindex):
        if not facility_ids:
            return

        # Reindex ONLY the affected locations. Never fall through to
        # index_facilities_new([]), which would reindex every facility.
        facility_ids = list(facility_ids)

        if not reindex:
            self.stdout.write(self.style.WARNING(
                f'Skipping reindex (--no-reindex) for {len(facility_ids)} '
                'location(s). Run a targeted reindex to refresh the API '
                'index.'
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[DRY-RUN] Would reindex {len(facility_ids)} location(s).'
            ))
            return

        self.stdout.write(
            f'Reindexing {len(facility_ids)} affected location(s)...'
        )
        index_facilities_new(facility_ids)
        self.stdout.write(self.style.SUCCESS(
            f'Reindexed {len(facility_ids)} location(s).'
        ))
