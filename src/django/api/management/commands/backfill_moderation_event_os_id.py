from django.core.management.base import BaseCommand
from opensearchpy.exceptions import ConnectionError, NotFoundError

from api.models.moderation_event import ModerationEvent
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from api.views.v1.index_names import OpenSearchIndexNames

BATCH_SIZE = 100
SCROLL_TIMEOUT = '2m'


class Command(BaseCommand):
    help = (
        'Backfills os_id into OpenSearch for approved moderation events '
        'where it is missing due to the signal writing the wrong field name.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Show how many events would be updated without '
                'actually writing to OpenSearch.'
            )
        )

    def __get_uuids_missing_os_id(self, opensearch):
        """Scroll through OpenSearch to find approved events missing os_id."""
        query = {
            'size': BATCH_SIZE,
            '_source': ['moderation_id'],
            'query': {
                'bool': {
                    'must': [
                        {'term': {'status': 'APPROVED'}},
                    ],
                    'must_not': [
                        {'exists': {'field': 'os_id'}},
                    ],
                }
            },
        }

        response = opensearch.client.search(
            index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            body=query,
            scroll=SCROLL_TIMEOUT,
        )

        uuids = []
        scroll_id = response['_scroll_id']

        while True:
            hits = response['hits']['hits']
            if not hits:
                break
            uuids.extend(
                hit['_source']['moderation_id'] for hit in hits
            )
            response = opensearch.client.scroll(
                scroll_id=scroll_id,
                scroll=SCROLL_TIMEOUT,
            )
            scroll_id = response['_scroll_id']

        opensearch.client.clear_scroll(scroll_id=scroll_id)
        return uuids

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        opensearch = OpenSearchServiceConnection()

        self.stdout.write(
            'Scanning OpenSearch for approved events missing os_id...'
        )
        uuids = self.__get_uuids_missing_os_id(opensearch)
        count = len(uuids)

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No events missing os_id in OpenSearch.')
            )
            return

        self.stdout.write(f'Found {count} events missing os_id.')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {count} events. '
                    'Run without --dry-run to write to OpenSearch.'
                )
            )
            return

        updated = 0
        skipped = 0

        for i in range(0, count, BATCH_SIZE):
            batch_uuids = uuids[i:i + BATCH_SIZE]
            events = ModerationEvent.objects.filter(
                uuid__in=batch_uuids,
                os_id__isnull=False,
            ).values('uuid', 'os_id')

            for event in events:
                try:
                    opensearch.client.update(
                        index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
                        id=str(event['uuid']),
                        body={'doc': {'os_id': event['os_id']}},
                    )
                    updated += 1
                except NotFoundError:
                    skipped += 1
                except ConnectionError as e:
                    self.stderr.write(
                        self.style.ERROR(f'Connection error: {e}')
                    )
                    raise

            self.stdout.write(
                f'Progress: {min(i + BATCH_SIZE, count)}/{count}'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Updated: {updated}, '
                f'not found in OpenSearch: {skipped}.'
            )
        )
