from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    """
    Replace index_claim_info with a version that includes updated_at
    (the claim's last-modified timestamp) so the claimed section can
    display the latest edit date rather than the original claim date.
    See OSDEV-2679.
    """
    helper.run_sql_files([
        '0218_index_claim_info.sql'
    ])


def revert_indexing_function(apps, schema_editor):
    helper.run_sql_files([
        '0203_index_claim_info.sql'
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0217_add_contribution_dates_to_index_contributors'),
    ]

    operations = [
        RunPython(update_indexing_function, revert_indexing_function)
    ]
