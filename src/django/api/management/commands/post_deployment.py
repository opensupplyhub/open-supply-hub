from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Each worker is a full Django subprocess (~150–200 MB RSS).
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Local': 2,
    'Development': 2,
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
        # Temporary for 2.28.0 (OSDEV-2949) — one-time cleanup that strips the
        # nested 'internal_ID' (not part of the partner field JSON Schema) from
        # 'rsc_grievance_mechanism' values. The ExtendedField database trigger
        # refreshes the affected FacilityIndex rows. Remove after the release
        # has been deployed everywhere.
        call_command('remove_rsc_grievance_mechanism_nested_internal_ids')
        # Temporary for OSDEV-2977 — recompute claim_info and approved_claim
        # without closing_date. Remove after the release has been deployed
        # everywhere.
        call_command(
            'backfill_facility_index',
            fields='claim_info,approved_claim',
            parallel=backfill_parallel_worker_count(),
            batch_size=10000,
        )
