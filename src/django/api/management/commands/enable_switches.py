from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: Enable the necessary switches, especially during the '
            'database reset.')

    def handle(self, *args, **options):
        call_command('waffle_switch', 'vector_tile', 'on')
        call_command('waffle_switch', 'claim_a_facility', 'on')
        call_command('waffle_switch', 'report_a_facility', 'on')
        call_command('waffle_switch', 'embedded_map', 'on')
        call_command('waffle_switch', 'extended_profile', 'on')
        call_command('waffle_switch', 'disable_list_uploading', 'off')
        call_command('waffle_switch', 'private_instance', 'off')
