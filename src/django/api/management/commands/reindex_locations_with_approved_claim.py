from django.core.management.base import BaseCommand

from api.constants import FacilityClaimStatuses
from api.models.facility.facility_claim import FacilityClaim
from api.models.transactions.index_facilities_new import index_facilities_new


class Command(BaseCommand):
    help = (
        'Reindexes only those locations that have approved claims.'
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

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        self.stdout.write(
            'Searching for approved claims...'
        )

        location_ids = list(
            FacilityClaim.objects
            .filter(status=FacilityClaimStatuses.APPROVED)
            .values_list('facility_id', flat=True)
            .distinct()
        )

        if not location_ids:
            self.stdout.write(
                self.style.WARNING(
                    'No locations found with approved claims.'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {len(location_ids)} locations with '
                'approved claims.'
            )
        )

        if dry_run:
            # In dry-run mode, show which locations would be reindexed.
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
        else:
            # Actually perform the reindexing.
            self.stdout.write('\nStarting reindex operation...')
            index_facilities_new(location_ids)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully reindexed {len(location_ids)} '
                    'locations with approved claims.'
                )
            )
