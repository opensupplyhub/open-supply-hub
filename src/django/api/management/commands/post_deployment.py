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
        # Temporary for 2.28.0 (OSDEV-2949) — one-time cleanup that strips the
        # nested 'internal_ID' (not part of the partner field JSON Schema) from
        # 'rsc_grievance_mechanism' values. The ExtendedField database trigger
        # refreshes the affected FacilityIndex rows. Remove after the release
        # has been deployed everywhere.
        call_command('remove_rsc_grievance_mechanism_nested_internal_ids')
