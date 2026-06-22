import logging

from django.core.management.base import BaseCommand

from api.models.facility.facility_list_item import FacilityListItem
from api.models.moderation_event import ModerationEvent

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Best-effort recovery of os_id_snapshot for approved ModerationEvents '
        'whose os_id was nulled by the SET_NULL cascade when a facility was '
        'deleted or merged. Recovers the OS ID from the linked '
        'FacilityListItem (via the moderation_event link).\n\n'
        'NOTE: coverage of the historical backlog is very low — the '
        'FacilityListItem <-> moderation_event link was only added in 2.21.0 '
        'with no backfill, so most events have no usable link and stay '
        'unrecoverable (~16 of ~36k on an Apr 2026 prod dump). Run with '
        '--dry-run to see counts before writing.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Show how many events would be recovered without '
                'actually writing to the database.'
            )
        )

    def __get_os_id_map_from_facility_list_items(self, target_uuids):
        """
        Look up os_id via FacilityListItem.facility_id for events that have a
        linked list item. Returns a dict of {uuid_str: facility_id}.
        """
        items = FacilityListItem.objects.filter(
            moderation_event__uuid__in=target_uuids,
            facility_id__isnull=False,
        ).values('moderation_event__uuid', 'facility_id')

        return {
            str(row['moderation_event__uuid']): row['facility_id']
            for row in items
        }

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        qs = ModerationEvent.objects.filter(
            status=ModerationEvent.Status.APPROVED,
            os_id__isnull=True,
            os_id_snapshot='',
        ).values_list('uuid', flat=True)

        target_uuids = list(qs)
        total = len(target_uuids)

        self.stdout.write(
            f'Found {total} approved events with null os_id and empty '
            'os_id_snapshot to recover.'
        )

        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nothing to recover.'))
            return

        self.stdout.write('Looking up os_id via FacilityListItem...')
        recovered_map = self.__get_os_id_map_from_facility_list_items(
            target_uuids
        )
        recoverable = len(recovered_map)
        unrecoverable = total - recoverable

        self.stdout.write(
            f'  FacilityListItem: found os_id for {recoverable} events.'
        )
        self.stdout.write(
            f'Total recoverable: {recoverable}, '
            f'unrecoverable: {unrecoverable}.'
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would write os_id_snapshot for '
                    f'{recoverable} events. '
                    'Run without --dry-run to apply changes.'
                )
            )
            return

        updated = 0
        failed_uuids = []
        for uuid, recovered_os_id in recovered_map.items():
            try:
                rows = ModerationEvent.objects.filter(
                    uuid=uuid,
                    status=ModerationEvent.Status.APPROVED,
                    os_id__isnull=True,
                    os_id_snapshot='',
                ).update(os_id_snapshot=recovered_os_id)
                updated += rows
            except Exception:
                failed_uuids.append(uuid)
                log.exception('Failed to update event %s', uuid)

        log.info(
            'Recovery backfill complete. Updated %s rows, '
            '%s unrecoverable, %s failed.',
            updated,
            unrecoverable,
            len(failed_uuids),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Recovered {updated} events. '
                f'{unrecoverable} events could not be recovered '
                '(no linked FacilityListItem with an os_id).'
            )
        )
        if failed_uuids:
            self.stderr.write(
                self.style.ERROR(
                    f'Failed to update {len(failed_uuids)} events. '
                    f'First failures: {failed_uuids[:10]}'
                )
            )
