from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Serves the free-text `q` filter, which had no index path at all: the
# leading `%` rules out the btree on name, and Django's own `__unaccent`
# emits the STABLE `unaccent()`, which Postgres refuses to index. The
# expression below is exactly what the ORM emits through the
# `immutable_unaccent` transform, because the planner only uses an
# expression index when the expression matches the predicate. Names are
# schema-qualified so pg_restore can rebuild this index with an empty
# search_path (OSDEV-3714). See OSDEV-3793.
INDEXES = {
    'api_facilityindex_name_search_trgm': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_name_search_trgm '
        'ON api_facilityindex USING gin ('
        'UPPER(public.immutable_unaccent(name::text)) gin_trgm_ops)'
    ),
}


def create_name_search_index(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_name_search_index(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, and it
    # keeps api_facilityindex writable while the index builds (see 0255).
    atomic = False

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
    ]

    operations = [
        RunPython(create_name_search_index, drop_name_search_index),
    ]
