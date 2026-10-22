from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_taxonomy_columns_to_claim_trigger(apps, schema_editor):
    """
    OSDEV-3430 (follow-up to OSDEV-3428). index_facility_type and
    index_processing_type count extended fields attached to an APPROVED
    claim, so the facility_type and processing_type index columns also
    depend on api_facilityclaim. perform_facility_claim_indexing was
    never updated for that dependency, leaving both columns stale when
    a claim is approved or revoked without extended fields changing.
    """
    helper.run_sql_files([
        '0236_add_taxonomy_columns_to_claim_trigger.sql',
    ])


def revert_taxonomy_columns_in_claim_trigger(apps, schema_editor):
    helper.run_sql_files([
        '0236_revert_taxonomy_columns_in_claim_trigger.sql',
    ])


class Migration(Migration):
    dependencies = [
        ('api', '0235_fix_taxonomy_index_triggers'),
    ]

    operations = [
        RunPython(
            add_taxonomy_columns_to_claim_trigger,
            revert_taxonomy_columns_in_claim_trigger,
        ),
    ]
