from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from django.utils import timezone

from api.models.extended_field import ExtendedField


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
        "(ExtendedField.value['{raw}']['{key}']) so the key is no longer "
        "returned by "
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

    @transaction.atomic
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']

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

        stats = {
            'scanned': 0,
            'updated': 0,
            'would_update': 0,
            'skipped': 0,
        }
        to_update = []

        def flush_batch():
            if not to_update:
                return
            if dry_run:
                stats['would_update'] += len(to_update)
                to_update.clear()
                return
            try:
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

            if len(to_update) >= batch_size:
                flush_batch()

            now = timezone.now()
            if (now - last_log).total_seconds() >= 10:
                self.stdout.write(
                    f"Progress: scanned={stats['scanned']} "
                    f"updated={stats['updated']} "
                    f"would_update={stats['would_update']} "
                    f"skipped={stats['skipped']}"
                )
                last_log = now

        flush_batch()

        if stats['scanned'] == 0:
            self.stdout.write(self.style.SUCCESS(
                f"No '{self.FIELD_NAME}' records contain a nested "
                f"'{self.INTERNAL_ID_KEY}'; nothing to do."
            ))
            return

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            f"Done{' [DRY-RUN]' if dry_run else ''}. "
            f"scanned={stats['scanned']} "
            f"updated={stats['updated']} "
            f"would_update={stats['would_update']} "
            f"skipped={stats['skipped']}"
        ))
