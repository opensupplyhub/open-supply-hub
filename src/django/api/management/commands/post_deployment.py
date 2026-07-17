from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Usage: This management command runs the Django migrations during "
        "the deployment process. It could be expanded to include other "
        "post-deployment tasks."
    )

    def handle(self, *args, **options):
        call_command("migrate")
