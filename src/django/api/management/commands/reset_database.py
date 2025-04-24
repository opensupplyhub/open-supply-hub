from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: This management command resets the database and '
            'repopulates it with fixture data.')

    def handle(self, *args, **options):
        call_command('recreate_db_structure')
        call_command('enable_switches')
        call_command('process_fixtures')
        call_command('assign_groups')
        call_command(
            'make_token',
            user_id=2,
            is_admin=True,
            token_key='1d18b962d6f976b0b7e8fcf9fcc39b56cf278051'
        )
        call_command(
            'make_token',
            user_id=3,
            is_admin=False,
            token_key='4c2e09b7a3f81e6c9d723f0ebdac15a47f1cb3da'
        )
