import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models.moderation_event import ModerationEvent

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Backfill os_id_snapshot on approved ModerationEvent rows where '
        'os_id_snapshot is empty but os_id is still present.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Show how many events would be updated without '
                'actually writing to the database.'
            )
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        qs = ModerationEvent.objects.filter(
            status=ModerationEvent.Status.APPROVED,
            os_id_snapshot='',
            os_id__isnull=False,
        )

        total = qs.count()
        log.info(
            'Backfilling os_id_snapshot for %s ModerationEvent rows.', total
        )
        self.stdout.write(
            f'Backfilling os_id_snapshot for {total} rows...'
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {total} events. '
                    'Run without --dry-run to apply changes.'
                )
            )
            return

        updated = 0
        for event in qs.iterator(chunk_size=1000):
            with transaction.atomic():
                event.os_id_snapshot = event.os_id
                event.save(update_fields=['os_id_snapshot'])
                updated += 1

        log.info('Backfill complete. Updated %s rows.', updated)
        self.stdout.write(self.style.SUCCESS(
            f'Done. Updated {updated} rows.'
        ))
