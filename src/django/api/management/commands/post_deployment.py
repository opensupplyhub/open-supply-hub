from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Temporary for 2.28.0 (OSDEV-1034). Each backfill worker is a full Django
# subprocess (~150-200 MB RSS), so size parallelism to the CLI task memory.
# Remove this map, the helper below, and the backfill call once the release
# has been deployed everywhere.
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Development': 2,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}


def backfill_parallel_worker_count() -> int:
    return BACKFILL_PARALLEL_BY_ENVIRONMENT.get(settings.ENVIRONMENT, 2)


class Command(BaseCommand):
    help = (
        "Usage: This management command runs the Django migrations during "
        "the deployment process. It could be expanded to include other "
        "post-deployment tasks."
    )

    def handle(self, *args, **options):
        call_command('migrate')
        # Temporary for 2.28.0 (OSDEV-2949) — one-time cleanup that strips the
        # nested 'internal_ID' (not part of the partner field JSON Schema) from
        # 'rsc_grievance_mechanism' values. The ExtendedField database trigger
        # refreshes the affected FacilityIndex rows. Remove after the release
        # has been deployed everywhere.
        call_command('remove_rsc_grievance_mechanism_nested_internal_ids')
        # Temporary for 2.28.0 (OSDEV-1034) — migration 0220 changes
        # index_processing_type(), so refresh the FacilityIndex.processing_type
        # column for facilities that have processing_type extended fields.
        # Remove after the release has been deployed everywhere.
        call_command(
            'backfill_facility_index',
            fields='processing_type',
            parallel=backfill_parallel_worker_count(),
            batch_size=10000,
        )
