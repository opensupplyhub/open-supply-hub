from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: This management command runs the Django migrations during '
            'the deployment process. It could be expanded to include other '
            'post-deployment tasks.')

    def handle(self, *args, **options):
        call_command('migrate')
        call_command('reindex_database')
        call_command('reindex_locations_with_environmental_data')
