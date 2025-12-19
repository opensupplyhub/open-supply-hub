from django.core.management import call_command
from django.core.management.base import (BaseCommand,
                                         CommandError)


class Command(BaseCommand):
    help = (
        'Load fixture data for the development and local environments, '
        'as well as the integration test database.'
    )

    def handle(self, *args, **options):
        try:
            call_command('loaddata',
                         'users.json',
                         'contributors.json',
                         'sources.json',
                         'facility_lists.json',
                         'sectors.json',
                         'moderation_events.json',
                         'us_county_tigerline.json')
        except CommandError as e:
            self.stderr.write("Error loading fixture data: {}".format(e))
