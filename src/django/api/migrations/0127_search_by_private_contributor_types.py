from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def search_by_private_contributor_types(apps, schema_editor):
    helper.run_sql_files([
        '0127_index_facilities_by.sql',
        '0127_index_facilities.sql',
    ])


def revert_search_by_private_contributor_types(apps, schema_editor):
    helper.run_sql_files([
        '0123_index_facilities_by.sql',
        '0123_index_facilities.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0126_add_tables_a_b_test'),
    ]

    operations = [
        RunPython(search_by_private_contributor_types, revert_search_by_private_contributor_types),
    ]
