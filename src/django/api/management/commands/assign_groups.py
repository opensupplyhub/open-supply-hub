from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: Assign groups to the user created during the database '
            'reset.')

    def handle(self, *args, **options):
        call_command('user_groups', '-e', 'c2@example.com', '-a', 'add', '-g',
                     'can_submit_facility')
        call_command('user_groups', '-e', 'c2@example.com', '-a', 'add', '-g',
                     'can_submit_private_facility')
        call_command('user_groups', '-e', 'c2@example.com', '-a', 'add', '-g',
                     'can_get_facility_history')
        call_command('user_groups', '-e', 'c2@example.com', '-a', 'add', '-g',
                     'can_view_full_contrib_detail')
