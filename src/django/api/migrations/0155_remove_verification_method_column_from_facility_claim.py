from django.db import connection
from django.db.migrations import RemoveField, Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    '''
    This function replaces the old index_approved_claim function with a
    similar one that does not index verification_method field.
    '''

    helper.run_sql_files(['0155_index_approved_claim.sql'])


class Migration(Migration):
    '''
    Since the verification_method field is no longer necessary for the
    claim form and isn't used anywhere in the codebase, it should be deleted
    from the FacilityClaim model and the respective history table.
    '''

    dependencies = [
        ('api', '0154_associate_sectors_with_groups'),
    ]

    operations = [
        RunPython(update_indexing_function),
        RemoveField(
            model_name='facilityclaim',
            name='verification_method',
        ),

        RemoveField(
            model_name='historicalfacilityclaim',
            name='verification_method',
        ),
    ]
