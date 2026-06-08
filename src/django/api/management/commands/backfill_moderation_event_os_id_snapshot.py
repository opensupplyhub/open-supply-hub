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

    def handle(self, *args, **options):
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
