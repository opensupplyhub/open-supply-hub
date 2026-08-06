from django.core.management.base import BaseCommand, CommandError

from api.constants import ProcessingAction
from api.models.facility.facility import Facility
from api.models.transactions.index_facilities_new import index_facilities_new


class Command(BaseCommand):
    help = (
        'Backfill (OSDEV-2896): reindexes locations whose canonical '
        '(created_from) contribution was promoted, so the name/address '
        'attribution reflects the promoted contributor. Only needed once, '
        'for locations promoted before the fix; new promotes self-heal via '
        'the indexing trigger.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Show which locations would be reindexed without '
                'actually doing it.'
            )
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of locations to reindex per batch (default: 500).'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        batch_size = options['batch_size']
        if batch_size < 1:
            raise CommandError('--batch-size must be a positive integer.')

        self.stdout.write('Searching for promoted locations...')

        location_ids = list(
            Facility.objects
            .filter(created_from__processing_results__contains=[
                {'action': ProcessingAction.PROMOTE_MATCH}
            ])
            .values_list('id', flat=True)
            .distinct()
        )

        if not location_ids:
            self.stdout.write(
                self.style.WARNING('No promoted locations found.')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {len(location_ids)} promoted locations.'
            )
        )

        if dry_run:
            self.stdout.write('\nLocation IDs that would be reindexed:')
            for location_id in location_ids:
                self.stdout.write(f'  - {location_id}')
            self.stdout.write(
                self.style.WARNING(
                    f'\nDRY RUN: Would reindex {len(location_ids)} '
                    'locations. Run without --dry-run to perform the '
                    'reindexing.'
                )
            )
            return

        self.stdout.write('\nStarting reindex operation...')
        total = len(location_ids)
        for start in range(0, total, batch_size):
            batch = location_ids[start:start + batch_size]
            index_facilities_new(batch)
            self.stdout.write(
                f'  Reindexed {min(start + batch_size, total)}/{total}'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reindexed {total} promoted locations.'
            )
        )
