from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# Serves the sector overlap filter, which had no index path at all even
# though sector is a primary facet of the search UI: `db_index=True` on the
# ArrayField declares the index on the *inner* field, which Django ignores,
# so the column reads as indexed and is not. Every sector-filtered search
# therefore scanned the whole of api_facilityindex.
#
# A plain GIN is enough because the ORM emits `sector && ARRAY[...]` and
# the values pass through unmodified from a controlled taxonomy. That is
# unlike facility_type, which is cleaned before matching and so needs the
# lower_varchar_array twin alongside its plain index.
#
# Measured on a 2,537,087-row anonymized restore, filtering to Aerospace
# and grouping by country: 5,757 ms -> 8.3 ms. Index size 11 MB.
# See OSDEV-3793 for the sibling trigram index on name.
INDEXES = {
    'api_facilityindex_sector_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_sector_gin '
        'ON api_facilityindex USING gin (sector)'
    ),
}


def create_sector_index(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_sector_index(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, and it
    # keeps api_facilityindex writable while the index builds (see 0255).
    atomic = False

    dependencies = [
        ('api', '0271_index_facility_name_search'),
    ]

    operations = [
        RunPython(create_sector_index, drop_sector_index),
    ]
