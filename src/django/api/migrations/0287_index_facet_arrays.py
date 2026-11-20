from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

# The three remaining array facets of the search filter, served the same
# way sector is by 0286: the ORM emits `column && ARRAY[...]` and a plain
# GIN answers the overlap directly, with values passed through unmodified.
#
# Measured on a 2,537,087-row anonymized restore, counting the most common
# value of each column:
#   product_type        38,443 rows   7,175 ms -> 730 ms
#   parent_company_name    514 rows   6,660 ms -> 6 ms
# A search narrowed only by one of these columns read the whole table.
# See OSDEV-3897.
INDEXES = {
    'api_facilityindex_product_type_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_product_type_gin '
        'ON api_facilityindex USING gin (product_type)'
    ),
    'api_facilityindex_number_of_workers_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_number_of_workers_gin '
        'ON api_facilityindex USING gin (number_of_workers)'
    ),
    'api_facilityindex_parent_company_name_gin': (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'api_facilityindex_parent_company_name_gin '
        'ON api_facilityindex USING gin (parent_company_name)'
    ),
}


def create_facet_indexes(apps, schema_editor):
    helper.create_indexes_concurrently('api_facilityindex', INDEXES)


def drop_facet_indexes(apps, schema_editor):
    helper.drop_indexes_concurrently(INDEXES)


class Migration(Migration):
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, and it
    # keeps api_facilityindex writable while the indexes build (see 0255).
    atomic = False

    dependencies = [
        ('api', '0286_index_sector_search'),
    ]

    operations = [
        RunPython(create_facet_indexes, drop_facet_indexes),
    ]
