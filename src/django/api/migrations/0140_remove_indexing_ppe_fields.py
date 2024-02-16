from api.migrations._migration_helper import MigrationHelper

from django.db import connection
from django.db.migrations import Migration, RunPython

helper = MigrationHelper(connection)


def update_indexing_functions(apps, schema_editor):
    '''
    This function replaces the old index_facilities and
    index_facilities_by functions with similar ones that do not
    index ppe fields.
    '''

    helper.run_sql_files([
        '0140_index_facilities.sql',
        '0140_index_facilities_by.sql'
        ])


def revert_updating_indexing_functions(apps, schema_editor):
    '''
    This function reverts the changes made by update_indexing_functions
    by running the SQL files for the previous version of indexing functions.
    '''
    helper.run_sql_files([
        '0130_index_facilities.sql',
        '0130_index_facilities_by.sql'
        ])


class Migration(Migration):

    dependencies = [
        ('api', '0139_remove_ppe_switch'),
    ]

    operations = [
        RunPython(update_indexing_functions,
                  revert_updating_indexing_functions)
    ]
