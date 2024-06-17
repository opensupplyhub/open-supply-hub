from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reindex the database.'

    def handle(self, *args, **options):
        self.stdout.write('Reindexing the database opensupplyhub...')
        with connection.cursor() as cursor:
            cursor.execute('REINDEX DATABASE opensupplyhub;')
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully reindexed the database opensupplyhub'
            )
        )
