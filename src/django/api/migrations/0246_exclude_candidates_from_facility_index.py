from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def exclude_candidates_from_facility_index(apps, schema_editor):
    """
    OSDEV-3243. Re-creates index_facilities_by(ids) and index_facilities()
    so that candidate facilities (api_facility.is_candidate = true, 0237)
    never get an api_facilityindex row. index_facilities_by is what the
    api_facility INSERT/UPDATE/DELETE triggers call, so after this
    migration a candidate is skipped on insert, inserted when it graduates
    (is_candidate -> false), removed when it reverts (-> true) and removed
    on delete. Any candidate rows already in the index are deleted.
    """
    helper.run_sql_files([
        '0246_index_facilities_exclude_candidates.sql',
    ])


def include_candidates_in_facility_index(apps, schema_editor):
    helper.run_sql_files([
        '0246_revert_index_facilities_exclude_candidates.sql',
    ])


class Migration(Migration):
    dependencies = [
        ('api', '0245_add_claim_quality_check_switch'),
    ]

    operations = [
        RunPython(
            exclude_candidates_from_facility_index,
            include_candidates_in_facility_index,
        ),
    ]
