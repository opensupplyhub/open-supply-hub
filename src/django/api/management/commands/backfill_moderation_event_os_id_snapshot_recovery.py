import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from opensearchpy.exceptions import ConnectionError, NotFoundError

from api.models.facility.facility_list_item import FacilityListItem
from api.models.moderation_event import ModerationEvent
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from api.views.v1.index_names import OpenSearchIndexNames

log = logging.getLogger(__name__)

BATCH_SIZE = 100


class Command(BaseCommand):
    help = (
        'Recovers os_id_snapshot for approved ModerationEvents where '
        'os_id was nulled by a cascading SET_NULL and os_id_snapshot is '
        'empty. Uses OpenSearch as the primary source (it was not updated '
        'by SET_NULL) and FacilityListItem as a fallback.'
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

    def __get_os_id_map_from_opensearch(self, target_uuids, opensearch):
        """
        Fetch os_id values from OpenSearch for the given set of UUIDs.
        Returns a dict of {uuid_str: os_id}.
        """
        os_id_map = {}
        uuid_list = list(str(u) for u in target_uuids)

        for i in range(0, len(uuid_list), BATCH_SIZE):
            batch = uuid_list[i:i + BATCH_SIZE]
            query = {
                'size': BATCH_SIZE,
                '_source': ['moderation_id', 'os_id'],
                'query': {
                    'bool': {
                        'must': [
                            {'terms': {'moderation_id': batch}},
                            {'exists': {'field': 'os_id'}},
                        ]
                    }
                },
            }
            try:
                response = opensearch.client.search(
                    index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
                    body=query,
                )
                for hit in response['hits']['hits']:
                    source = hit['_source']
                    mid = source.get('moderation_id')
                    oid = source.get('os_id')
                    if mid and oid:
                        os_id_map[mid] = oid
            except (ConnectionError, NotFoundError) as e:
                self.stderr.write(
                    self.style.ERROR(
                        f'OpenSearch error on batch {i}-{i+BATCH_SIZE}: {e}'
                    )
                )

        return os_id_map

    def __get_os_id_map_from_facility_list_items(self, target_uuids):
        """
        Fallback: look up os_id via FacilityListItem.facility_id for events
        that have a linked list item.
        Returns a dict of {uuid_str: facility_id}.
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

        opensearch = OpenSearchServiceConnection()

        self.stdout.write('Querying OpenSearch for os_id values...')
        os_id_map = self.__get_os_id_map_from_opensearch(
            target_uuids, opensearch
        )
        self.stdout.write(
            f'  OpenSearch: found os_id for {len(os_id_map)} events.'
        )

        still_missing = [
            u for u in target_uuids if str(u) not in os_id_map
        ]
        fallback_map = {}
        if still_missing:
            self.stdout.write(
                f'  {len(still_missing)} events not found in OpenSearch. '
                'Trying FacilityListItem fallback...'
            )
            fallback_map = self.__get_os_id_map_from_facility_list_items(
                still_missing
            )
            self.stdout.write(
                f'  FacilityListItem fallback: found {len(fallback_map)} '
                'additional events.'
            )

        combined_map = {**os_id_map, **fallback_map}
        recoverable = len(combined_map)
        unrecoverable = total - recoverable

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
        for uuid, recovered_os_id in combined_map.items():
            with transaction.atomic():
                rows = ModerationEvent.objects.filter(
                    uuid=uuid,
                    os_id__isnull=True,
                    os_id_snapshot='',
                ).update(os_id_snapshot=recovered_os_id)
                updated += rows

        log.info(
            'Recovery backfill complete. Updated %s rows, '
            '%s unrecoverable.',
            updated,
            unrecoverable,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Recovered {updated} events. '
                f'{unrecoverable} events could not be recovered '
                '(no os_id in OpenSearch or FacilityListItem).'
            )
        )
