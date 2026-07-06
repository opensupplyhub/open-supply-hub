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
        call_command('reindex_database')
        # Temporary for 2.27.0 — remove after the code freeze is complete and
        # the release has been deployed everywhere.
        call_command(
            'backfill_facility_index',
            fields='contributors',
            parallel=backfill_parallel_worker_count(),
            batch_size=10000,
        )
        # Temporary for 2.27.0 (OSDEV-2896) — one-time backfill of name/address
        # attribution for facilities promoted before the OSDEV-2197 fix. Remove
        # after the release has been deployed everywhere.
        call_command('reindex_promoted_locations')
