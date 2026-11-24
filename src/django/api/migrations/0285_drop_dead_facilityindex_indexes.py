from django.db import connection, migrations, models
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Four indexes on api_facilityindex that production never reads, verified
# against pg_stat_user_indexes over an 87-day window (counters since
# 2026-08-28, read 2026-11-23): every one had idx_scan = 0.
#
#   - Both address btrees (399 MB each): no predicate in the search filter
#     touches address at all.
#   - The name varchar_pattern_ops twin (228 MB): free-text search matches
#     through UPPER(immutable_unaccent(name)), which these cannot serve.
#   - The facility_type lower GIN (19 MB): orphaned by a code change; the
#     exact-match path emits lower_varchar_array(processing_type) only,
#     and facility_type matches against the raw column.
#
# NOT dropped, although the same hypothesis once named them: the
# varchar_pattern_ops twins on id and country_code, which serve plain
# equality and are among the hottest indexes on the table (299 billion
# and 130 million scans in the same window), and the plain name btree
# (171 scans; something rare reads it). Evidence on OSDEV-3898.
#
# api_facilityindex is trigger-rewritten from seven tables and updated_at
# is indexed, so HOT never applies: every write maintains every index.
# These drops remove ~1.05 GB of maintenance on the two widest columns,
# offsetting the trigram index added by OSDEV-3793.
INDEXES = {
    'api_facilityindexnew_address_f7bdbae6': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindexnew_address_f7bdbae6 '
        'ON api_facilityindex USING btree (address)'
    ),
    'api_facilityindexnew_address_f7bdbae6_like': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindexnew_address_f7bdbae6_like '
        'ON api_facilityindex USING btree (address varchar_pattern_ops)'
    ),
    'api_facilityindexnew_name_0c3f20cb_like': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindexnew_name_0c3f20cb_like '
        'ON api_facilityindex USING btree (name varchar_pattern_ops)'
    ),
    'api_facilityindex_facility_type_lower_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_facility_type_lower_gin '
        'ON api_facilityindex USING gin '
        '(lower_varchar_array(facility_type))'
    ),
}


def drop_dead_indexes(apps, schema_editor):
    helper.drop_indexes_concurrently(list(INDEXES))


def recreate_dead_indexes(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


class Migration(Migration):
    # DROP/CREATE INDEX CONCURRENTLY cannot run inside a transaction, and
    # concurrent drops never block api_facilityindex's writes (see 0255).
    atomic = False

    dependencies = [
        ('api', '0284_zone_set_last_upload_sha256'),
    ]

    operations = [
        # The address field no longer declares db_index, so Django's model
        # state agrees with the database once the drops run; the name field
        # keeps db_index=True because only its varchar_pattern_ops twin is
        # dead, and that twin is not represented in model state.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='facilityindex',
                    name='address',
                    field=models.CharField(
                        max_length=300,
                        null=False,
                        blank=False,
                        help_text=(
                            'The full street address of the facility.'
                        ),
                    ),
                ),
            ],
            database_operations=[
                RunPython(drop_dead_indexes, recreate_dead_indexes),
            ],
        ),
    ]
