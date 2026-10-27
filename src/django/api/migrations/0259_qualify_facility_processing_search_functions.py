from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def qualify_facility_processing_search_functions(apps, schema_editor):
    """
    Schema-qualify the bodies of the two search helpers 0233 (OSDEV-3189)
    added, so pg_restore can rebuild the expression indexes that inline them
    under the empty search path every dump sets.
    """
    helper.run_sql_files([
        '0259_qualify_facility_processing_search_functions.sql',
    ])


def revert_qualify_facility_processing_search_functions(apps, schema_editor):
    helper.run_sql_files([
        '0259_revert_qualify_facility_processing_search_functions.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0258_facility_claim_isic'),
    ]

    operations = [
        RunPython(
            qualify_facility_processing_search_functions,
            revert_qualify_facility_processing_search_functions,
        ),
    ]
