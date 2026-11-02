from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# One multicolumn GIN index per revision serves the ISIC overlap filters on
# any level. Without them every ISIC search reads the whole of
# api_facilityindex.
INDEXES = {
    'api_facilityindex_isic_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS api_facilityindex_isic_gin '
        'ON api_facilityindex USING gin '
        '(isic_section, isic_division, isic_group, isic_class)'
    ),
    'api_facilityindex_isic5_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS api_facilityindex_isic5_gin '
        'ON api_facilityindex USING gin '
        '(isic5_section, isic5_division, isic5_group, isic5_class)'
    ),
}


def create_isic_index(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_isic_index(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, and it
    # keeps api_facilityindex writable while the index builds (see 0233).
    atomic = False

    dependencies = [
        ('api', '0254_add_isic_taxonomy'),
    ]

    operations = [
        RunPython(create_isic_index, drop_isic_index),
    ]
