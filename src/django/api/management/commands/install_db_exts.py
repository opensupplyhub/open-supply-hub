from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = ('Install all the necessary PostgreSQL extensions for the '
            'database. The command is idempotent and can be re-run safely. '
            'Every extension is attempted, and the command exits non-zero if '
            'any of them failed.')

    extensions = (
        'btree_gin',
        'pg_trgm',
        'postgis',
        'unaccent',
        'pgcrypto',
        # pgaudit provides the database activity auditing required by SOC 2.
        # It can only be created once the library is loaded at server start,
        # so the RDS instance must already have been rebooted after pgaudit
        # was added to shared_preload_libraries, and pgaudit.log must still be
        # "none" at that point -- see doc/ops/database-auditing.md. pgaudit is
        # not available in the local postgres:16 image, so this command exits
        # non-zero outside AWS.
        'pgaudit',
    )

    def handle(self, *args, **options):
        failed = []

        for extension_name in self.extensions:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'CREATE EXTENSION IF NOT EXISTS {extension_name};')
                    self.stdout.write(self.style.SUCCESS(
                        f'{extension_name} extension installed successfully.'
                    ))
            except Exception as e:
                failed.append(extension_name)
                self.stderr.write(self.style.ERROR(
                    ('An error occurred during '
                     f'the installation of {extension_name}: {e}')
                ))

        if failed:
            raise CommandError(
                'Failed to install the following extensions: '
                f"{', '.join(failed)}. The database is not fully configured; "
                'see the errors above.'
            )
