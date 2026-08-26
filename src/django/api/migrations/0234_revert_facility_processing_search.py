from django.db import connection
from django.db.migrations import (
    DeleteModel,
    Migration,
    RunPython,
    SeparateDatabaseAndState,
)
from psycopg2 import sql

from api.migrations._migration_helper import MigrationHelper


helper = MigrationHelper(connection)

SEARCH_INDEXES = {
    'api_facilityindex_facility_type_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_facility_type_gin '
        'ON api_facilityindex USING gin (facility_type)'
    ),
    'api_facilityindex_processing_type_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_processing_type_gin '
        'ON api_facilityindex USING gin (processing_type)'
    ),
    'api_facilityindex_processing_type_lower_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_processing_type_lower_gin '
        'ON api_facilityindex USING gin (lower_varchar_array(processing_type))'
    ),
    'api_facilityindex_facility_type_lower_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_facility_type_lower_gin '
        'ON api_facilityindex USING gin (lower_varchar_array(facility_type))'
    ),
    'api_facilityindex_fp_search_trgm': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_fp_search_trgm '
        'ON api_facilityindex USING gin ('
        'facility_processing_search_text(facility_type, processing_type) '
        'gin_trgm_ops)'
    ),
    'api_facility_processing_value_search_trgm': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facility_processing_value_search_trgm '
        'ON api_facility_processing_value USING gin ('
        'kind, immutable_unaccent(lower(value)) gin_trgm_ops)'
    ),
}

DROP_INDEX_CONCURRENTLY_SQL = sql.SQL(
    'DROP INDEX CONCURRENTLY IF EXISTS {}'
)

INVALID_INDEXES_SQL = """
    SELECT cls.relname
    FROM pg_index idx
    JOIN pg_class cls ON cls.oid = idx.indexrelid
    WHERE NOT idx.indisvalid
      AND cls.relname = ANY(%s)
"""


def drop_invalid_search_indexes():
    """Remove interrupted concurrent builds before retrying index creation."""
    with connection.cursor() as cursor:
        cursor.execute(INVALID_INDEXES_SQL, [list(SEARCH_INDEXES)])
        invalid_indexes = [row[0] for row in cursor.fetchall()]

        for index_name in invalid_indexes:
            cursor.execute(
                DROP_INDEX_CONCURRENTLY_SQL.format(
                    sql.Identifier(index_name)
                )
            )


def drop_search_indexes_and_functions(apps, schema_editor):
    """Remove the search indexes before dropping their helper functions."""
    with connection.cursor() as cursor:
        for index_name in SEARCH_INDEXES:
            cursor.execute(
                DROP_INDEX_CONCURRENTLY_SQL.format(
                    sql.Identifier(index_name)
                )
            )

    helper.run_sql_files([
        '0233_revert_facility_processing_search_functions.sql',
    ])


def recreate_search_indexes_and_functions(apps, schema_editor):
    """Restore migration 0233 when this rollback migration is reversed."""
    with connection.cursor() as cursor:
        cursor.execute('CREATE EXTENSION IF NOT EXISTS btree_gin')

    helper.run_sql_files([
        '0233_facility_processing_search_functions.sql',
    ])
    drop_invalid_search_indexes()

    with connection.cursor() as cursor:
        for statement in SEARCH_INDEXES.values():
            cursor.execute(statement)

        cursor.execute('ANALYZE api_facilityindex')
        cursor.execute('ANALYZE api_facility_processing_value')


def drop_facility_processing_value_index(apps, schema_editor):
    """Remove the derived aggregate tables and their maintenance triggers."""
    helper.run_sql_files([
        '0232_revert_facility_processing_value_index.sql',
    ])


def recreate_facility_processing_value_index(apps, schema_editor):
    """Restore and repopulate migration 0232 when rolling this back."""
    # A failed non-atomic reverse can leave only some aggregate objects.
    # Clear those derived objects so retrying starts from a known state.
    helper.run_sql_files([
        '0232_revert_facility_processing_value_index.sql',
    ])
    helper.run_sql_files([
        '0232_facility_processing_value_index.sql',
    ])
    with connection.cursor() as cursor:
        cursor.execute('CALL recompute_facility_processing_values();')


def restore_legacy_indexing_functions(apps, schema_editor):
    """Restore the FacilityIndex function definitions used before PR #1217."""
    helper.run_sql_files([
        '0130_index_facility_type.sql',
        '0220_index_processing_type.sql',
    ])


def restore_processing_search_indexing_functions(apps, schema_editor):
    """Restore migration 0231 when this rollback migration is reversed."""
    helper.run_sql_files([
        '0231_index_facility_type.sql',
        '0231_index_processing_type.sql',
    ])


class Migration(Migration):
    # DROP/CREATE INDEX CONCURRENTLY cannot run in a transaction.
    atomic = False

    dependencies = [
        ('api', '0233_index_facility_processing_search'),
    ]

    operations = [
        RunPython(
            drop_search_indexes_and_functions,
            recreate_search_indexes_and_functions,
        ),
        SeparateDatabaseAndState(
            database_operations=[
                RunPython(
                    drop_facility_processing_value_index,
                    recreate_facility_processing_value_index,
                ),
            ],
            state_operations=[
                DeleteModel(name='FacilityProcessingValue'),
            ],
        ),
        RunPython(
            restore_legacy_indexing_functions,
            restore_processing_search_indexing_functions,
        ),
    ]
