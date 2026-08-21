import time

from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from django.db.models import F

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

    Each batch commits on its own, so no lock is held across the whole
    run. Every updated row fires the existing `api_extendedfield` trigger,
    which rebuilds the whole `FacilityIndex` summary for that row's
    facility -- so a facility with N drifted fields is rebuilt N times.
    Use `--sleep` to spread that load out, and expect the run to be paced
    by the reindex rather than by the update itself.

    The command is resumable: already-corrected rows stop matching, so a
    plain re-run continues where an interrupted run stopped.
    `--start-after-id` skips explicitly past a known id.
    """

    help = (
        'Re-attribute ExtendedField.contributor to the contributor of the '
        'Source the field was contributed through, for rows that drifted '
        'apart after a list source reassignment (OSDEV-2159). Commits per '
        'batch and is safe to re-run after an interruption.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of rows updated per committed batch (default: 500)'
        )
        parser.add_argument(
            '--sleep',
            type=float,
            default=0.0,
            help=(
                'Seconds to pause between batches, to throttle the '
                'reindexing the update triggers (default: 0)'
            )
        )
        parser.add_argument(
            '--start-after-id',
            type=int,
            default=0,
            help=(
                'Resume from an ExtendedField id, skipping every row at or '
                'below it (default: 0, meaning start from the beginning)'
            )
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help=(
                'Stop after processing this many rows, for timing a sample '
                'before committing to a full run (default: 0, no limit)'
            )
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Report what would change without writing to the database.'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        sleep_seconds = options['sleep']
        limit = options['limit']
        dry_run = options['dry_run']
        last_id = options['start_after_id']

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
        )

        remaining = base_qs.filter(id__gt=last_id).count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS(
                'Every extended field already matches the contributor of '
                'its source; nothing to do.'
            ))
            return

        facilities = (
            base_qs
            .filter(id__gt=last_id, facility__isnull=False)
            .values('facility_id')
            .distinct()
            .count()
        )
        self.stdout.write(
            f'{remaining} extended field(s) to re-attribute across '
            f'{facilities} location(s). Each row update triggers a full '
            f'FacilityIndex rebuild for its location.'
        )

        processed = 0
        batch_number = 0
        started_at = time.monotonic()

        while True:
            if limit and processed >= limit:
                self.stdout.write(self.style.WARNING(
                    f'Reached --limit {limit}; stopping early. '
                    f'Resume with --start-after-id {last_id}.'
                ))
                break

            size = batch_size
            if limit:
                size = min(batch_size, limit - processed)

            batch = list(
                base_qs
                .filter(id__gt=last_id)
                .select_related('facility_list_item__source')
                .order_by('id')[:size]
            )
            if not batch:
                break

            batch_number += 1
            batch_started_at = time.monotonic()

            for extended_field in batch:
                extended_field.contributor_id = (
                    extended_field.facility_list_item.source.contributor_id
                )

            if not dry_run:
                try:
                    with transaction.atomic():
                        ExtendedField.objects.bulk_update(
                            batch, ['contributor'], batch_size=size
                        )
                except DatabaseError as exc:
                    self.stderr.write(self.style.ERROR(
                        f'Batch {batch_number} failed after {processed} '
                        f'row(s): {exc}. Committed batches are kept; '
                        f'resume with --start-after-id {last_id}.'
                    ))
                    raise

            last_id = batch[-1].id
            processed += len(batch)

            self.stdout.write(
                f'Batch {batch_number}: {len(batch)} row(s) '
                f'(total {processed}/{remaining}, last_id={last_id}, '
                f'{time.monotonic() - batch_started_at:.1f}s)'
            )

            if sleep_seconds:
                time.sleep(sleep_seconds)

        elapsed = time.monotonic() - started_at
        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            f"Done{' [DRY-RUN]' if dry_run else ''}. "
            f'processed={processed} '
            f'batches={batch_number} '
            f'last_id={last_id} '
            f'elapsed={elapsed:.1f}s'
        ))
