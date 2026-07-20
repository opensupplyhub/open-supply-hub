from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Temporary for 2.27.0 — remove this map and the backfill_facility_index call
# below once the 2.27.0 code freeze is complete and the release has been
# deployed everywhere. See facility_index_backfill/README.md.
#
# Each worker is a full Django subprocess (~150–200 MB RSS).
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Development': 2,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}


def backfill_parallel_worker_count() -> int:
    """Return post-deploy backfill parallelism for the current environment.

    Temporary for 2.27.0 — remove with BACKFILL_PARALLEL_BY_ENVIRONMENT after
    the 2.27.0 code freeze is complete.
    """
    return BACKFILL_PARALLEL_BY_ENVIRONMENT[settings.ENVIRONMENT]


class Command(BaseCommand):
    help = ('Usage: This management command runs the Django migrations during '
            'the deployment process. It could be expanded to include other '
            'post-deployment tasks.')

    def handle(self, *args, **options):
        call_command('migrate')
        # Temporary for 2.28.0 (OSDEV-2949) — one-time cleanup that strips the
        # nested 'internal_ID' (not part of the partner field JSON Schema) from
        # 'rsc_grievance_mechanism' values and reindexes the affected
        # locations, so the key is no longer exposed by the API. Remove after
        # the release has been deployed everywhere.
        call_command('remove_rsc_grievance_mechanism_nested_internal_ids')
