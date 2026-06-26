from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Post-deploy backfill worker counts by environment. Each worker is a full
# Django subprocess (~150–200 MB RSS); see facility_index_backfill/README.md.
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Development': 2,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}


def backfill_parallel_worker_count() -> int:
    """Return post-deploy backfill parallelism for the current environment."""
    return BACKFILL_PARALLEL_BY_ENVIRONMENT[settings.ENVIRONMENT]


class Command(BaseCommand):
    help = ('Usage: This management command runs the Django migrations during '
            'the deployment process. It could be expanded to include other '
            'post-deployment tasks.')

    def handle(self, *args, **options):
        call_command('migrate')
        call_command('reindex_database')
        call_command(
            'backfill_facility_index',
            fields='contributors',
            parallel=backfill_parallel_worker_count(),
            batch_size=10000,
        )
