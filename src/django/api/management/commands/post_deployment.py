from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Usage: This management command runs the Django migrations during "
        "the deployment process. It could be expanded to include other "
        "post-deployment tasks."
    )

    def handle(self, *args, **options):
        call_command('migrate')

        # One-time data fix for OSDEV-2159. Re-attributes extended fields
        # whose contributor drifted from the contributor of the source
        # they were contributed through, which happened whenever a list's
        # `Source.contributor` was reassigned before 2.29.0. Remove this
        # call after this release has been deployed everywhere.
        call_command('backfill_extended_field_contributors')
