from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from django.db.models import F
from django.utils import timezone

from api.models.extended_field import ExtendedField


class Command(BaseCommand):
    """
    One-off data fix for OSDEV-2159.

    Before OSDEV-2159, reassigning `Source.contributor` (typically in
    Django admin, when a list is moved to a different contributor) left
    `ExtendedField.contributor` pointing at the original uploader. Those
    extended fields keep showing the old contributor on facility detail
    pages, in search responses and in downloads.

    This command re-attributes every extended field whose contributor no
    longer matches the contributor of the source it came from. Extended
    fields created from a FacilityClaim have no `facility_list_item` and
    are left untouched.
    """

    help = (
        'Re-attribute ExtendedField.contributor to the contributor of the '
        'Source the field was contributed through, for rows that drifted '
        'apart after a list source reassignment (OSDEV-2159).'
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

        # A source whose contributor was cleared cannot be propagated:
        # ExtendedField.contributor is NOT NULL.
        base_qs = (
            ExtendedField.objects
            .filter(
                facility_list_item__isnull=False,
                facility_list_item__source__contributor__isnull=False,
            )
            .exclude(
                contributor=F('facility_list_item__source__contributor')
            )
            .select_related('facility_list_item__source')
            .order_by('id')
        )

        stats = {
            'scanned': 0,
            'updated': 0,
            'would_update': 0,
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
                    to_update, ['contributor'], batch_size=batch_size
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

            extended_field.contributor_id = (
                extended_field.facility_list_item.source.contributor_id
            )
            to_update.append(extended_field)

            if len(to_update) >= batch_size:
                flush_batch()

            now = timezone.now()
            if (now - last_log).total_seconds() >= 10:
                self.stdout.write(
                    f"Progress: scanned={stats['scanned']} "
                    f"updated={stats['updated']} "
                    f"would_update={stats['would_update']}"
                )
                last_log = now

        flush_batch()

        if stats['scanned'] == 0:
            self.stdout.write(self.style.SUCCESS(
                'Every extended field already matches the contributor of '
                'its source; nothing to do.'
            ))
            return

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            f"Done{' [DRY-RUN]' if dry_run else ''}. "
            f"scanned={stats['scanned']} "
            f"updated={stats['updated']} "
            f"would_update={stats['would_update']}"
        ))
