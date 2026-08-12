from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = ('Install all the necessary PostgreSQL extensions for the '
            'database. The command is idempotent and can be re-run safely.')

    extensions = (
        'btree_gin',
        'pg_trgm',
        'postgis',
        'unaccent',
        'pgcrypto',
        # pgaudit provides the database activity auditing required by SOC 2.
        # It can only be created once the library is loaded at server start,
        # which means the RDS instance must already have been rebooted after
        # pgaudit was added to shared_preload_libraries -- see
        # doc/ops/database-auditing.md. Until then this one extension fails
        # with "pgaudit must be loaded via shared_preload_libraries"; the
        # error is logged and the remaining extensions still install.
        'pgaudit',
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
