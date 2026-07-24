from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_functions(apps, schema_editor):
    """
    Remove closing_date from index_claim_info and index_approved_claim JSON
    output so claim closing dates are no longer exposed via API or downloads.
    See OSDEV-2977.
    """
    helper.run_sql_files([
        '0220_remove_closing_date_from_index_claim_info.sql',
        '0220_remove_closing_date_from_index_approved_claim.sql',
    ])


def revert_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0218_index_claim_info.sql',
        '0207_index_approved_claim.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0219_add_contributor_anonymise_in_paid_products'),
    ]

    operations = [
        RunPython(update_indexing_functions, revert_indexing_functions)
    ]
