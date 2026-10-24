from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Serves isic_4 searches that opt in to mapped values (OSDEV-3382), as
# api_facilityindex_isic_gin (0255) serves the submitted ones.
INDEXES = {
    'api_facilityindex_isic_mapped_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_isic_mapped_gin '
        'ON api_facilityindex USING gin (isic_mapped_section, '
        'isic_mapped_division, isic_mapped_group, isic_mapped_class)'
    ),
}


def create_isic_mapped_index(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_isic_mapped_index(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction (see 0233).
    atomic = False

    dependencies = [
        ('api', '0256_isic_crosswalk'),
    ]

    operations = [
        RunPython(create_isic_mapped_index, drop_isic_mapped_index),
    ]
