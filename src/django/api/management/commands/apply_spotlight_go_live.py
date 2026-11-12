from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models.spotlight_field import SpotlightField


class Command(BaseCommand):
    help = (
        'Switches on every approved Spotlight field for partners whose '
        'go-live date has arrived. Runs once per date, so a partner who '
        'later turns a field off is not overridden. Meant to run daily.'
    )

    def handle(self, *args, **options):
        """Activate approved fields for every go-live date that is due."""
        due = SpotlightField.objects.filter(
            go_live_date__lte=timezone.localdate(),
            go_live_applied=False,
        )
        total = 0
        for field_set in due:
            total += field_set.apply_go_live()
        self.stdout.write(
            f'Spotlight go-live: {due.count()} field set(s) due, '
            f'{total} field(s) activated.'
        )
