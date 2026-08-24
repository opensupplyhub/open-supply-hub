from django.db.migrations import Migration, RunPython
from django.db import connection
from psycopg2 import sql

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Every index is built CONCURRENTLY: api_facilityindex is written one row at a
# time by the indexing triggers of half a dozen tables, and a regular CREATE
# INDEX would block those writes for the whole build.
INDEXES = {
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
    # kind leads the index (through btree_gin) so the typeahead reads only the
    # rows of the kind it asked for. Without it the planner has to intersect a
    # trigram scan with the primary key, which costs more than reading the
    # whole table.
    'api_facility_processing_value_search_trgm': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facility_processing_value_search_trgm '
        'ON api_facility_processing_value USING gin ('
        'kind, immutable_unaccent(lower(value)) gin_trgm_ops)'
    ),
}

# Created by migration 0228 before the typeahead searched the normalized
# value; nothing can use an index on the raw one.
UNUSED_INDEXES = ('api_facility_processing_value_value_trgm_idx',)

ANALYZED_TABLES = ('api_facilityindex', 'api_facility_processing_value')

INVALID_INDEXES_SQL = """
    SELECT
        cls.relname
    FROM
        pg_index idx
    JOIN pg_class cls ON cls.oid = idx.indexrelid
    WHERE
        NOT idx.indisvalid
        AND cls.relname = ANY(%s)
"""


def _drop_invalid_indexes(index_names):
    """
    Drop leftovers of an interrupted concurrent build.

    A failed CREATE INDEX CONCURRENTLY leaves an invalid index behind that
    the planner ignores but that IF NOT EXISTS still counts as present, so a
    retry would otherwise silently skip the rebuild.
    """
    with connection.cursor() as cursor:
        cursor.execute(INVALID_INDEXES_SQL, [list(index_names)])
        invalid = [row[0] for row in cursor.fetchall()]

        for index_name in invalid:
            cursor.execute(
                sql.SQL('DROP INDEX CONCURRENTLY IF EXISTS {}').format(
                    sql.Identifier(index_name)
                )
            )


def index_facility_processing_search(apps, schema_editor):
    """
    Index the facility and processing type values the search filters read.

    Neither the facility_type nor the processing_type array of
    api_facilityindex had an index, so every location search filtering on them
    scanned the whole table. The taxonomy filters use array overlap, which a
    plain GIN index serves directly. The case-insensitive filter behind the
    processing type typeahead overlaps the lower-cased array instead, and the
    free-text filter matches a word-prefix regex that only trigrams can
    narrow, so both need an expression index. The typeahead's own candidate
    query gets one too, over the normalized value it actually searches. See
    OSDEV-3189.
    """
    helper.run_sql_files([
        '0229_facility_processing_search_functions.sql',
    ])

    _drop_invalid_indexes(INDEXES)

    with connection.cursor() as cursor:
        for index_name in UNUSED_INDEXES:
            cursor.execute(
                sql.SQL('DROP INDEX CONCURRENTLY IF EXISTS {}').format(
                    sql.Identifier(index_name)
                )
            )

        for statement in INDEXES.values():
            cursor.execute(statement)

        # An expression index has no statistics until the table is analyzed,
        # and without them the planner misjudges how selective these filters
        # are. ANALYZE takes only a SHARE UPDATE EXCLUSIVE lock, so ordinary
        # writes are unaffected.
        for table_name in ANALYZED_TABLES:
            cursor.execute(
                sql.SQL('ANALYZE {}').format(sql.Identifier(table_name))
            )


def revert_facility_processing_search_index(apps, schema_editor):
    with connection.cursor() as cursor:
        for index_name in INDEXES:
            cursor.execute(
                sql.SQL('DROP INDEX CONCURRENTLY IF EXISTS {}').format(
                    sql.Identifier(index_name)
                )
            )

    helper.run_sql_files([
        '0229_revert_facility_processing_search_functions.sql',
    ])


class Migration(Migration):

    # CREATE INDEX CONCURRENTLY cannot run inside a transaction block, and
    # Django wraps migrations in one by default.
    atomic = False

    dependencies = [
        ('api', '0228_create_facility_processing_value_index'),
    ]

    operations = [
        RunPython(
            index_facility_processing_search,
            revert_facility_processing_search_index,
        )
    ]
