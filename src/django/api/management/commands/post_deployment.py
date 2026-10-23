from django.core.management import call_command
from django.core.management.base import BaseCommand

from api.facility_index_backfill.utils import backfill_parallel_worker_count


class Command(BaseCommand):
    help = (
        "Usage: This management command runs the Django migrations during "
        "the deployment process. It could be expanded to include other "
        "post-deployment tasks."
    )

    def handle(self, *args, **options):
        call_command('migrate')
        # One-time ISIC backfill for Release 2.33.0; remove once it has run
        # in every environment.
        call_command(
            'backfill_facility_index',
            fields='isic_4,isic_4_mapped',
            parallel=backfill_parallel_worker_count(),
            batch_size=10000,
        )
