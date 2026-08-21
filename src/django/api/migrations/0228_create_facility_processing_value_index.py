from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def create_facility_processing_value_index(apps, schema_editor):
    """
    Create the api_facility_processing_value table and its delta triggers.

    Aggregating the facility_type and processing_type arrays of
    api_facilityindex on every request takes seconds over 2.5M rows, so the
    processing type typeahead reads distinct values and their location counts
    from this table instead. The counts follow api_facilityindex through
    triggers, which keeps them accurate without a scheduled rebuild. Junk
    sentinels such as the literal string 'null' are excluded here so they
    never reach suggestions, even for rows indexed before the sentinels were
    filtered out during indexing. See OSDEV-3189.
    """
    helper.run_sql_files([
        '0228_facility_processing_value_index.sql',
    ])


def drop_facility_processing_value_index(apps, schema_editor):
    helper.run_sql_files([
        '0228_revert_facility_processing_value_index.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0227_index_facility_processing_raw_values'),
    ]

    operations = [
        RunPython(
            create_facility_processing_value_index,
            drop_facility_processing_value_index,
        )
    ]
