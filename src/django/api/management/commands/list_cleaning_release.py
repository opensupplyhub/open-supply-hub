from django.core.management.base import BaseCommand

from api.services.list_cleaning import sweep_lapsed


class Command(BaseCommand):
    help = ('Close every list-cleaning review window that has lapsed '
            '(OSDEV-3726 v3). The lists concerned go through as uploaded. '
            'Lapses are also noticed lazily whenever a list is read, so '
            'this only matters for lists nobody looks at.')

    def handle(self, *args, **options):
        closed = sweep_lapsed()
        self.stdout.write(f'Closed {closed} lapsed review window(s).')
