from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = ('Install all the necessary PostgreSQL extensions for the database '
            'based on the required DB extensions for the 1.7.0 release.')

    extensions = (
        'btree_gin',
        'pg_trgm',
        'postgis',
        'unaccent',
        'pgcrypto',
    )

    def handle(self, *args, **options):
        for extension_name in self.extensions:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'CREATE EXTENSION IF NOT EXISTS {extension_name};')
                    self.stdout.write(self.style.SUCCESS(
                        f'{extension_name} extension installed successfully.'
                    ))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    ('An error occurred during '
                     f'the installation of {extension_name}: {e}')
                ))
