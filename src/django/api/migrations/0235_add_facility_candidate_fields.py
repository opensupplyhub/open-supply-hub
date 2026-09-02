import django.contrib.gis.db.models.fields
from django.db import migrations, models
from django.db.models import Q
from psycopg2 import sql

IS_CANDIDATE_HELP_TEXT = (
    'Whether this facility is an unconfirmed candidate created by an '
    'automated detection source (e.g. satellite imagery) rather than a '
    'confirmed, named facility.'
)
POLYGON_HELP_TEXT = (
    'The detected footprint of a candidate facility in WGS 84 (EPSG:4326).'
)
CONFIDENCE_HELP_TEXT = (
    'The detection confidence score reported by the automated source for a '
    'candidate facility.'
)
EXTERNAL_ID_HELP_TEXT = (
    'The identifier of this facility in the external source system, used '
    'together with source for ingest idempotency.'
)
SOURCE_HELP_TEXT = (
    'The external detection source that created this facility as a '
    'candidate (e.g. earth_genome). Empty for facilities created through '
    'the normal contribution flow.'
)

# api_facility and api_historicalfacility hold millions of rows and take
# writes continuously (every facility save appends a history row), so every
# index is built CONCURRENTLY: a regular CREATE INDEX would block those
# writes for the whole build. The unique index backs the
# api_facility_source_external_id_uniq constraint attached below.
INDEXES = {
    'api_facility_is_candidate_idx': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facility_is_candidate_idx '
        'ON api_facility (is_candidate)'
    ),
    'api_facility_polygon_gist': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facility_polygon_gist '
        'ON api_facility USING gist (polygon)'
    ),
    'api_facility_source_external_id_uniq': (
        'CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facility_source_external_id_uniq '
        'ON api_facility (source, external_id)'
    ),
    'api_historicalfacility_is_candidate_idx': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_historicalfacility_is_candidate_idx '
        'ON api_historicalfacility (is_candidate)'
    ),
    'api_historicalfacility_polygon_gist': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_historicalfacility_polygon_gist '
        'ON api_historicalfacility USING gist (polygon)'
    ),
}

ANALYZED_TABLES = ('api_facility', 'api_historicalfacility')

DROP_INDEX_CONCURRENTLY_SQL = sql.SQL(
    'DROP INDEX CONCURRENTLY IF EXISTS {}'
)

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


def _drop_invalid_indexes(connection, index_names):
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
                DROP_INDEX_CONCURRENTLY_SQL.format(
                    sql.Identifier(index_name)
                )
            )


def create_candidate_indexes(apps, schema_editor):
    """
    Build the indexes the new candidate columns need, without blocking
    writes: the filter index on is_candidate, the spatial indexes Django
    would have created for the PolygonField on both tables, and the unique
    index that backs the (source, external_id) constraint.

    Uses schema_editor.connection (not django.db.connection) so the work
    lands on whichever database alias the migration is running against.
    """
    connection = schema_editor.connection
    _drop_invalid_indexes(connection, INDEXES)

    with connection.cursor() as cursor:
        for statement in INDEXES.values():
            cursor.execute(statement)

        # The new columns have no statistics until the tables are analyzed,
        # and without them the planner misjudges how selective an
        # is_candidate filter is. ANALYZE takes only a SHARE UPDATE
        # EXCLUSIVE lock, so ordinary writes are unaffected.
        for table_name in ANALYZED_TABLES:
            cursor.execute(
                sql.SQL('ANALYZE {}').format(sql.Identifier(table_name))
            )


def drop_candidate_indexes(apps, schema_editor):
    # The unique index is normally gone by now: reversing the constraint
    # RunSQL below drops it together with the constraint. IF EXISTS covers
    # the case where the constraint was never attached.
    with schema_editor.connection.cursor() as cursor:
        for index_name in INDEXES:
            cursor.execute(
                DROP_INDEX_CONCURRENTLY_SQL.format(
                    sql.Identifier(index_name)
                )
            )


class Migration(migrations.Migration):

    # CREATE INDEX CONCURRENTLY cannot run inside a transaction block, and
    # Django wraps migrations in one by default.
    atomic = False

    dependencies = [
        ('api', '0234_add_note_type_to_facility_claim_review_note'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # The database side is written by hand (inline RunSQL +
            # RunPython) instead of plain AddField/AddConstraint because
            # both tables are huge: adding the columns with a DEFAULT is a
            # metadata-only change on Postgres 11+, but the indexes and the
            # unique constraint must be built CONCURRENTLY so writes are
            # never blocked.
            database_operations=[
                # Every ALTER TABLE here takes an ACCESS EXCLUSIVE lock.
                # Each is metadata-only and instant once acquired, but a
                # long transaction touching the table would make the ALTER
                # queue — and all later reads/writes queue behind it. The
                # lock_timeout makes the ALTER fail fast instead; every
                # statement is idempotent (IF NOT EXISTS / DO-block
                # guards), so the recovery is simply rerunning migrate.
                migrations.RunSQL(
                    sql=[
                        "SET lock_timeout = '5s';",
                        '''
                        ALTER TABLE api_facility
                        ADD COLUMN IF NOT EXISTS
                            is_candidate boolean NOT NULL DEFAULT false,
                        ADD COLUMN IF NOT EXISTS
                            polygon geometry(Polygon,4326) NULL,
                        ADD COLUMN IF NOT EXISTS
                            confidence double precision NULL,
                        ADD COLUMN IF NOT EXISTS
                            external_id varchar(200) NULL,
                        ADD COLUMN IF NOT EXISTS
                            source varchar(200) NOT NULL DEFAULT '';
                        ''',
                        '''
                        ALTER TABLE api_historicalfacility
                        ADD COLUMN IF NOT EXISTS
                            is_candidate boolean NOT NULL DEFAULT false,
                        ADD COLUMN IF NOT EXISTS
                            polygon geometry(Polygon,4326) NULL,
                        ADD COLUMN IF NOT EXISTS
                            confidence double precision NULL,
                        ADD COLUMN IF NOT EXISTS
                            external_id varchar(200) NULL,
                        ADD COLUMN IF NOT EXISTS
                            source varchar(200) NOT NULL DEFAULT '';
                        ''',
                        # The DB defaults are kept on purpose — Django's
                        # AddField would drop them, but dedupe-hub writes
                        # api_facility through its own SQLAlchemy model
                        # that predates these columns, so its INSERTs must
                        # keep succeeding (as non-candidates) until
                        # OSDEV-3243 teaches it the new schema. Same
                        # pattern as 0234's NOT NULL DEFAULT.
                        'RESET lock_timeout;',
                    ],
                    reverse_sql=[
                        "SET lock_timeout = '5s';",
                        '''
                        ALTER TABLE api_historicalfacility
                        DROP COLUMN IF EXISTS is_candidate,
                        DROP COLUMN IF EXISTS polygon,
                        DROP COLUMN IF EXISTS confidence,
                        DROP COLUMN IF EXISTS external_id,
                        DROP COLUMN IF EXISTS source;
                        ''',
                        '''
                        ALTER TABLE api_facility
                        DROP COLUMN IF EXISTS is_candidate,
                        DROP COLUMN IF EXISTS polygon,
                        DROP COLUMN IF EXISTS confidence,
                        DROP COLUMN IF EXISTS external_id,
                        DROP COLUMN IF EXISTS source;
                        ''',
                        'RESET lock_timeout;',
                    ],
                ),
                migrations.RunPython(
                    create_candidate_indexes,
                    drop_candidate_indexes,
                ),
                # Attaching a constraint to an already-built unique index is
                # a metadata-only ALTER TABLE, so the ACCESS EXCLUSIVE lock
                # it takes is held only for an instant. Postgres has no ADD
                # CONSTRAINT IF NOT EXISTS, hence the DO-block guard, which
                # keeps a retry of this non-atomic migration idempotent.
                migrations.RunSQL(
                    sql=[
                        "SET lock_timeout = '5s';",
                        '''
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1
                                FROM pg_constraint
                                WHERE conname =
                                    'api_facility_source_external_id_uniq'
                                AND conrelid = 'api_facility'::regclass
                            ) THEN
                                ALTER TABLE api_facility
                                ADD CONSTRAINT
                                    api_facility_source_external_id_uniq
                                UNIQUE USING INDEX
                                    api_facility_source_external_id_uniq;
                            END IF;
                        END $$;
                        ''',
                        # NULLs are distinct in the unique index (normal
                        # facilities depend on that), so it cannot stop a
                        # sourced row from re-ingesting with no id: any row
                        # claiming an external source must carry that
                        # source's id. NOT VALID keeps the ACCESS EXCLUSIVE
                        # lock instant; VALIDATE scans with only a SHARE
                        # UPDATE EXCLUSIVE lock (writes unaffected) and is
                        # a no-op on retry.
                        '''
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1
                                FROM pg_constraint
                                WHERE conname =
                                    'api_facility_source_requires_external_id'
                                AND conrelid = 'api_facility'::regclass
                            ) THEN
                                ALTER TABLE api_facility
                                ADD CONSTRAINT
                                    api_facility_source_requires_external_id
                                CHECK (
                                    source = ''
                                    OR external_id IS NOT NULL
                                ) NOT VALID;
                            END IF;
                        END $$;
                        ''',
                        '''
                        ALTER TABLE api_facility
                        VALIDATE CONSTRAINT
                            api_facility_source_requires_external_id;
                        ''',
                        'RESET lock_timeout;',
                    ],
                    reverse_sql=[
                        "SET lock_timeout = '5s';",
                        '''
                        ALTER TABLE api_facility
                        DROP CONSTRAINT IF EXISTS
                            api_facility_source_requires_external_id;
                        ''',
                        '''
                        ALTER TABLE api_facility
                        DROP CONSTRAINT IF EXISTS
                            api_facility_source_external_id_uniq;
                        ''',
                        'RESET lock_timeout;',
                    ],
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='facility',
                    name='is_candidate',
                    field=models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text=IS_CANDIDATE_HELP_TEXT,
                    ),
                ),
                migrations.AddField(
                    model_name='facility',
                    name='polygon',
                    field=django.contrib.gis.db.models.fields.PolygonField(
                        blank=True,
                        help_text=POLYGON_HELP_TEXT,
                        null=True,
                        srid=4326,
                    ),
                ),
                migrations.AddField(
                    model_name='facility',
                    name='confidence',
                    field=models.FloatField(
                        blank=True,
                        help_text=CONFIDENCE_HELP_TEXT,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name='facility',
                    name='external_id',
                    field=models.CharField(
                        blank=True,
                        help_text=EXTERNAL_ID_HELP_TEXT,
                        max_length=200,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name='facility',
                    name='source',
                    field=models.CharField(
                        blank=True,
                        default='',
                        help_text=SOURCE_HELP_TEXT,
                        max_length=200,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacility',
                    name='is_candidate',
                    field=models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text=IS_CANDIDATE_HELP_TEXT,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacility',
                    name='polygon',
                    field=django.contrib.gis.db.models.fields.PolygonField(
                        blank=True,
                        help_text=POLYGON_HELP_TEXT,
                        null=True,
                        srid=4326,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacility',
                    name='confidence',
                    field=models.FloatField(
                        blank=True,
                        help_text=CONFIDENCE_HELP_TEXT,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacility',
                    name='external_id',
                    field=models.CharField(
                        blank=True,
                        help_text=EXTERNAL_ID_HELP_TEXT,
                        max_length=200,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacility',
                    name='source',
                    field=models.CharField(
                        blank=True,
                        default='',
                        help_text=SOURCE_HELP_TEXT,
                        max_length=200,
                    ),
                ),
                migrations.AddConstraint(
                    model_name='facility',
                    constraint=models.UniqueConstraint(
                        fields=('source', 'external_id'),
                        name='api_facility_source_external_id_uniq',
                    ),
                ),
                migrations.AddConstraint(
                    model_name='facility',
                    constraint=models.CheckConstraint(
                        check=Q(source='') | Q(external_id__isnull=False),
                        name='api_facility_source_requires_external_id',
                    ),
                ),
            ],
        ),
    ]
