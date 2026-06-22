from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: This management command runs the Django migrations during '
            'the deployment process. It could be expanded to include other '
            'post-deployment tasks.')

    def handle(self, *args, **options):
        call_command('migrate')
        call_command('reindex_database')
        # One-time, best-effort os_id_snapshot recovery for OSDEV-2878.
        # Remove after the 2.26.0 release has been deployed everywhere.
        call_command('backfill_moderation_event_os_id_snapshot_recovery')
