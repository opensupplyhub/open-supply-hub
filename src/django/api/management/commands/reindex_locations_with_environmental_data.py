from django.core.management.base import BaseCommand
from django.db.models import Q

from api.constants import FacilityClaimStatuses
from api.models.facility.facility_claim import FacilityClaim
from api.models.transactions.index_facilities_new import index_facilities_new


class Command(BaseCommand):
    help = (
        'Reindexes only those locations that have approved claims '
        'containing environmental data (energy consumption, throughput, '
        'opening/closing dates).'
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
            'Searching for approved claims with environmental data...'
        )

        # Query for approved location claims that have at least one
        # environmental field populated.
        environmental_fields_filter = (
            Q(opening_date__isnull=False) |
            Q(closing_date__isnull=False) |
            Q(estimated_annual_throughput__isnull=False) |
            Q(energy_coal__isnull=False) |
            Q(energy_natural_gas__isnull=False) |
            Q(energy_diesel__isnull=False) |
            Q(energy_kerosene__isnull=False) |
            Q(energy_biomass__isnull=False) |
            Q(energy_charcoal__isnull=False) |
            Q(energy_animal_waste__isnull=False) |
            Q(energy_electricity__isnull=False) |
            Q(energy_other__isnull=False)
        )

        approved_claims_with_env_data = (
            FacilityClaim.objects
            .filter(status=FacilityClaimStatuses.APPROVED)
            .filter(environmental_fields_filter)
            .select_related('facility')
            .distinct()
        )

        # Extract location IDs (facility_id field).
        location_ids = list(
            approved_claims_with_env_data.values_list('facility_id', flat=True)
        )

        if not location_ids:
            self.stdout.write(
                self.style.WARNING(
                    'No locations found with approved claims containing '
                    'environmental data.'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {len(location_ids)} locations with '
                'environmental data:'
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
                    'locations with environmental data.'
                )
            )
