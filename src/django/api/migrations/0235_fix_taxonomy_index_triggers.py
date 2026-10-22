from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_taxonomy_columns_to_dependent_triggers(apps, schema_editor):
    """
    OSDEV-3428. 0231 (OSDEV-3189) made the facility_type and
    processing_type index columns depend on api_facilitymatch and
    api_source, but the per-table indexing procedures for those tables
    (and api_facilitylistitem) were never taught to recompute them. Any
    event that changes matches or sources without touching extended
    fields leaves both columns stale — visibly, locations approved via
    a moderation event (v1 API / SLC) computed the columns before their
    FacilityMatch existed and stayed invisible to the Facility Type and
    Processing Type search filters.
    """
    helper.run_sql_files([
        '0235_add_taxonomy_columns_to_dependent_triggers.sql',
    ])


def revert_taxonomy_columns_in_dependent_triggers(apps, schema_editor):
    helper.run_sql_files([
        '0235_revert_taxonomy_columns_in_dependent_triggers.sql',
    ])


class Migration(Migration):
    dependencies = [
        ('api', '0234_add_note_type_to_facility_claim_review_note'),
    ]

    operations = [
        RunPython(
            add_taxonomy_columns_to_dependent_triggers,
            revert_taxonomy_columns_in_dependent_triggers,
        ),
    ]
