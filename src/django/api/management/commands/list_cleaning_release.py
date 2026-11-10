from django.core.management.base import BaseCommand

from api.services.list_cleaning import sweep_lapsed


class Command(BaseCommand):
    help = ('Close every list-cleaning review window that has lapsed and '
            'poll every run still waiting on the pipeline (OSDEV-3726 v3). '
            'A lapsed list goes through with what its contributor had '
            'decided (as uploaded if they never opened the review); a '
            'run that failed out there closes its window too. Both are '
            'also noticed lazily whenever a list is read or moderated, '
            'so this only matters for lists nobody looks at.')

    def handle(self, *args, **options):
        closed = sweep_lapsed()
        self.stdout.write(f'Closed {closed} lapsed review window(s).')
