from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    """
    Replace index_processing_type() so the searchable
    FacilityIndex.processing_type column stays aligned with the processing
    type shown on the location profile.

    The previous version gated matched_values entries on the field-type tag
    (raw ? 'PROCESSING_TYPE'), which dropped values that the taxonomy
    classifies as a facility type even though they are also valid processing
    types (e.g. "Final Product Assembly"). Such a value is stored in a
    processing_type ExtendedField and displayed under Processing Type, but was
    excluded from the search index, so filtering by it returned no results.

    The new version keeps every entry whose processing-type slot (index 3) is
    populated, mirroring the facility_type index (index 2) and the frontend
    display logic. See OSDEV-1034.
    """
    helper.run_sql_files([
        '0220_index_processing_type.sql'
    ])


def revert_indexing_function(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_processing_type.sql'
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0219_add_contributor_anonymise_in_paid_products'),
    ]

    operations = [
        RunPython(update_indexing_function, revert_indexing_function)
    ]
