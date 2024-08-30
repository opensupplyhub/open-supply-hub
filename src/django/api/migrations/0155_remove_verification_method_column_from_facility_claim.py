from django.db import connection
from django.db.migrations import Migration, RemoveField, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    '''
    This function replaces the old index_approved_claim function with a
    similar one that does not index verification_method and
    phone_number fields.
    '''
    helper.run_sql_files(['0155_index_approved_claim.sql'])


class Migration(Migration):
    '''
    This migration removes the verification_method and phone_number fields
    from the FacilityClaim and HistoricalFacilityClaim models.
    It also updates the indexing function accordingly.
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
            model_name='facilityclaim',
            name='phone_number',
        ),
        RemoveField(
            model_name='historicalfacilityclaim',
            name='verification_method',
        ),
        RemoveField(
            model_name='historicalfacilityclaim',
            name='phone_number',
        )
    ]
