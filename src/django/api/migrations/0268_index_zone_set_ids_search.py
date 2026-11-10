from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Serves the zone_set_ids overlap filter of a zone-set Spotlight partner
# search. Without it every such search reads the whole of
# api_facilityindex.
INDEXES = {
    'api_facilityindex_zone_set_ids_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_zone_set_ids_gin '
        'ON api_facilityindex USING gin (zone_set_ids)'
    ),
}


def create_zone_set_ids_index(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_zone_set_ids_index(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, and it
    # keeps api_facilityindex writable while the index builds (see 0255).
    atomic = False

    dependencies = [
        ('api', '0267_add_zone_set_ids_to_facility_index'),
    ]

    operations = [
        RunPython(create_zone_set_ids_index, drop_zone_set_ids_index),
    ]
