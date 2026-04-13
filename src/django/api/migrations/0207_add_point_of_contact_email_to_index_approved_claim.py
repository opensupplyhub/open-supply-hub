from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    """
    Replace index_approved_claim with a version that includes
    point_of_contact_email in the approved claim JSON, so the facility
    download can surface it in the claim_point_of_contact_email column.
    """
    helper.run_sql_files(['0207_index_approved_claim.sql'])


def revert_indexing_function(apps, schema_editor):
    helper.run_sql_files(['0155_index_approved_claim.sql'])


class Migration(Migration):

    dependencies = [
        ('api', '0206_backfill_claim_types_from_extended_fields'),
    ]

    operations = [
        RunPython(update_indexing_function, revert_indexing_function)
    ]
