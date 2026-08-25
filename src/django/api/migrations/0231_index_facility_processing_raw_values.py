from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_functions(apps, schema_editor):
    """
    Extend index_facility_type() and index_processing_type() so unmatched raw
    contributor values from profile-visible ExtendedFields are searchable.

    Each function keeps the existing standardized extraction from
    matched_values (indices 2 and 3) and falls back to the raw_values entry at
    the same position when that slot is null, mirroring process_raw_values()
    string vs array handling. Only ExtendedFields visible on the location
    profile are included (approved claim or active match with active source),
    matching index_extended_fields(). Both values come from one pass over the
    ExtendedFields of the location, because these functions run on every
    ExtendedField write. See OSDEV-3189.
    """
    helper.run_sql_files([
        '0231_index_facility_type.sql',
        '0231_index_processing_type.sql',
    ])


def revert_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_facility_type.sql',
        '0220_index_processing_type.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0230_setup_india_labour_line_partner_field'),
    ]

    operations = [
        RunPython(update_indexing_functions, revert_indexing_functions)
    ]
