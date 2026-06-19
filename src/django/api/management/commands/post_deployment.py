from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: This management command runs the Django migrations during '
            'the deployment process. It could be expanded to include other '
            'post-deployment tasks.')

    def handle(self, *args, **options):
<<<<<<< HEAD
        call_command('migrate')
        call_command('reindex_database')
=======
>>>>>>> b80a64c7 (Remove backfill from post_deployment and cap migrate at 0213.)
        call_command(
            'migrate',
            'api',
            '0213_add_partner_field_availability_flags',
        )
        # call_command('reindex_database')
