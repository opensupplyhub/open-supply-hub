from django.core.management.base import BaseCommand
from opensearchpy.exceptions import ConnectionError, NotFoundError

from api.models.moderation_event import ModerationEvent
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from api.views.v1.index_names import OpenSearchIndexNames


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

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        events = ModerationEvent.objects.filter(
            status=ModerationEvent.Status.APPROVED,
            os_id__isnull=False,
        ).values('uuid', 'os_id')

        count = events.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING('No approved events with os_id found.')
            )
            return

        self.stdout.write(f'Found {count} events to update.')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {count} events. '
                    'Run without --dry-run to write to OpenSearch.'
                )
            )
            return

        opensearch = OpenSearchServiceConnection()
        updated = 0
        skipped = 0

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
            self.style.SUCCESS(
                f'Done. Updated: {updated}, '
                f'not found in OpenSearch: {skipped}.'
            )
        )
