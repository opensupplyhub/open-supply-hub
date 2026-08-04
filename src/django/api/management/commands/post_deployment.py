from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Temporary for the OSDEV-1034 and OSDEV-2977 backfills. Each worker is a
# subprocess (~150-200 MB RSS), so size parallelism to the CLI task memory.
# Remove this map, the helper below, and the backfill call once the release
# has been deployed everywhere.
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Local': 2,
    'Development': 1,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}

# Fallback when settings.ENVIRONMENT is not in the map
# (e.g. a new deploy target).
BACKFILL_PARALLEL_DEFAULT = 2


def backfill_parallel_worker_count() -> int:
    return BACKFILL_PARALLEL_BY_ENVIRONMENT.get(
        settings.ENVIRONMENT,
        BACKFILL_PARALLEL_DEFAULT,
    )


class Command(BaseCommand):
    help = (
        "Usage: This management command runs the Django migrations during "
        "the deployment process. It could be expanded to include other "
        "post-deployment tasks."
    )

    def handle(self, *args, **options):
        call_command('migrate')
