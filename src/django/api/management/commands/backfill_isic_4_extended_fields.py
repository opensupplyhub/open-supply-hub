from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError, DatabaseError
from django.utils import timezone

from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.models.nonstandard_field import NonstandardField


class Command(BaseCommand):
    help = (
        "Backfill isic_4 values from FacilityListItem.raw_json into "
        "ExtendedField for items that are MATCHED or CONFIRMED_MATCH, "
        "where the contributor has a corresponding NonstandardField('isic_4')."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size', type=int, default=1000,
            help='Bulk insert batch size (default: 1000)'
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Do not write to DB; just report what would be done'
        )
        parser.add_argument(
            '--no-continue-on-error',
            action='store_false',
            dest='continue_on_error',
            default=True,
            help=(
                'On bulk insert error, stop instead of trying '
                'per-row inserts'
            )
        )
        parser.add_argument(
            '--contributor-id', type=int, default=None,
            help='Restrict to a single contributor_id'
        )
        parser.add_argument(
            '--reset', action='store_true', default=False,
            help="Delete existing isic_4 extended fields before backfill"
        )
        parser.add_argument(
            '--singleisic', action='store_true', default=False,
            help=(
                'If set, backfill only one isic_4 extended field and '
                'print the related facility OS ID'
            )
        )

    def handle(self, *args, **options):
        self.stdout.write('Backfilling isic_4 extended fields (ORM)...')

        batch_size = options['batch_size']
        dry_run = options['dry_run']
        continue_on_error = options['continue_on_error']
        contributor_filter = options['contributor_id']
        single_only = options['singleisic']

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY-RUN enabled: no database writes will be performed.'
            ))

        nsf_qs = NonstandardField.objects.filter(column_name='isic_4')
        if contributor_filter:
            nsf_qs = nsf_qs.filter(contributor_id=contributor_filter)

        contributor_ids = set(nsf_qs.values_list('contributor_id', flat=True))

        if not contributor_ids:
            self.stdout.write(
                'No contributors configured with isic_4; nothing to do.'
            )
            return

        # Optionally reset existing data first.
        if options['reset'] and not dry_run:
            reset_qs = ExtendedField.objects.filter(
                field_name=ExtendedField.ISIC_4
            )
            if contributor_filter:
                reset_qs = reset_qs.filter(
                    contributor_id__in=contributor_ids
                )
            deleted, _ = reset_qs.delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Reset: deleted {deleted} existing isic_4 rows."
                )
            )

        existing_fli_ids = set(
            ExtendedField.objects
            .filter(field_name=ExtendedField.ISIC_4)
            .values_list('facility_list_item_id', flat=True)
        )

        items_qs = (
            FacilityListItem.objects
            .select_related('source__contributor', 'facility')
            .filter(
                status__in=[
                    FacilityListItem.MATCHED,
                    FacilityListItem.CONFIRMED_MATCH,
                ],
                source__contributor_id__in=contributor_ids,
            )
            .filter(raw_json__has_key='isic_4')
            .exclude(id__in=existing_fli_ids)
            .order_by('id')
        )

        # If only one record should be backfilled, handle here and exit.
        if single_only:
            item = items_qs.first()
            if item is None:
                self.stdout.write(
                    'No eligible items found for single backfill.'
                )
                return

            raw = item.raw_json.get('isic_4')
            if raw in (None, '', []):
                self.stdout.write(
                    'Eligible item does not contain isic_4; nothing to do.'
                )
                return

            # Normalize value: if single-element list, unwrap to object;
            # if multiple elements, keep as list.
            if isinstance(raw, list):
                normalized_value = raw[0] if len(raw) == 1 else raw
            else:
                normalized_value = raw

            # Save in the same format as duns_id/lei_id/rba_id.
            value = {
                'raw_value': normalized_value,
            }

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "[DRY-RUN] Would backfill one isic_4 row for OS ID "
                        f"{item.facility.id}"
                    )
                )
                return

            try:
                with transaction.atomic():
                    ef = ExtendedField(
                        contributor=item.source.contributor,
                        facility=item.facility,
                        facility_list_item=item,
                        facility_claim=None,
                        is_verified=False,
                        field_name=ExtendedField.ISIC_4,
                        value=value,
                        origin_source=item.origin_source,
                    )
                    ef.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Backfilled 1 isic_4 row. OS ID: {item.facility.id}"
                    )
                )
            except (IntegrityError, DatabaseError) as exc:
                self.stderr.write(self.style.ERROR(
                    f'Failed to insert single isic_4 row: {exc}'
                ))
                raise
            return

        to_create = []
        stats = {
            'scanned': 0,
            'queued': 0,
            'inserted': 0,
            'would_insert': 0,
            'bulk_failures': 0,
            'row_failures': 0,
            'skipped_empty_value': 0,
        }

        def flush_batch():
            if not to_create:
                return
            nonlocal stats

            if dry_run:
                stats['would_insert'] += len(to_create)
                to_create.clear()
                return

            try:
                with transaction.atomic():
                    ExtendedField.objects.bulk_create(
                        to_create, batch_size=batch_size
                    )
                stats['inserted'] += len(to_create)
                to_create.clear()
            except (IntegrityError, DatabaseError) as exc:
                stats['bulk_failures'] += 1
                self.stderr.write(self.style.ERROR(
                    f'Bulk insert failed for batch of {len(to_create)}: {exc}'
                ))
                if not continue_on_error:
                    raise

                rows = list(to_create)
                to_create.clear()
                for row in rows:
                    try:
                        with transaction.atomic():
                            row.save()
                        stats['inserted'] += 1
                    except Exception as row_exc:
                        stats['row_failures'] += 1
                        self.stderr.write(
                            self.style.ERROR(
                                'Row insert failed '
                                f'(fli_id={row.facility_list_item_id}): '
                                f'{row_exc}'
                            )
                        )

        last_log = timezone.now()
        for item in items_qs.iterator(chunk_size=batch_size):
            stats['scanned'] += 1
            raw = item.raw_json.get('isic_4')
            if raw in (None, '', []):
                stats['skipped_empty_value'] += 1
                continue

            # Normalize value: if single-element list, unwrap to object;
            # if multiple elements, keep as list
            if isinstance(raw, list):
                normalized_value = raw[0] if len(raw) == 1 else raw
            else:
                normalized_value = raw

            # Save in the same format as duns_id/lei_id/rba_id.
            value = {
                'raw_value': normalized_value,
            }

            ef = ExtendedField(
                contributor=item.source.contributor,
                facility=item.facility,
                facility_list_item=item,
                facility_claim=None,
                is_verified=False,
                field_name=ExtendedField.ISIC_4,
                value=value,
                origin_source=item.origin_source,
            )
            to_create.append(ef)
            stats['queued'] += 1

            if len(to_create) >= batch_size:
                flush_batch()

            now = timezone.now()
            if (now - last_log).total_seconds() >= 10:
                if dry_run:
                    self.stdout.write(
                        "Progress [DRY-RUN]: "
                        f"scanned={stats['scanned']} "
                        f"queued={stats['queued']} "
                        f"would_insert={stats['would_insert']} "
                        f"bulk_failures={stats['bulk_failures']} "
                        f"row_failures={stats['row_failures']}"
                    )
                else:
                    self.stdout.write(
                        "Progress: "
                        f"scanned={stats['scanned']} "
                        f"queued={stats['queued']} "
                        f"inserted={stats['inserted']} "
                        f"bulk_failures={stats['bulk_failures']} "
                        f"row_failures={stats['row_failures']}"
                    )
                last_log = now

        flush_batch()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Done [DRY-RUN]. No changes written. "
                    f"scanned={stats['scanned']} queued={stats['queued']} "
                    f"would_insert={stats['would_insert']} inserted=0 "
                    f"bulk_failures={stats['bulk_failures']} "
                    f"row_failures={stats['row_failures']} "
                    f"skipped_empty_value={stats['skipped_empty_value']}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Done. "
                    f"scanned={stats['scanned']} queued={stats['queued']} "
                    f"inserted={stats['inserted']} "
                    f"bulk_failures={stats['bulk_failures']} "
                    f"row_failures={stats['row_failures']} "
                    f"skipped_empty_value={stats['skipped_empty_value']}"
                )
            )
