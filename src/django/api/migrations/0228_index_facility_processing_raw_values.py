from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_functions(apps, schema_editor):
    """
    Extend index_facility_type() and index_processing_type() so unmatched raw
    contributor values from profile-visible ExtendedFields are searchable.

    Each function keeps the existing standardized extraction from
    matched_values (indices 2 and 3) and UNIONs raw_values entries whose
    paired matched_values slot is null, mirroring process_raw_values() string
    vs array handling. Only ExtendedFields visible on the location profile
    are included (approved claim or active match with active source), matching
    index_extended_fields(). See OSDEV-3189.
    """
    helper.run_sql_files([
        '0226_index_facility_type.sql',
        '0226_index_processing_type.sql',
    ])


def revert_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_facility_type.sql',
        '0220_index_processing_type.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0227_create_isic_taxonomy_config'),
    ]

    operations = [
        RunPython(update_indexing_functions, revert_indexing_functions)
    ]
