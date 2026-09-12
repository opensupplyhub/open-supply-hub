from django.db import connection, models
from django.db.migrations import (
    CreateModel,
    Migration,
    RunPython,
    SeparateDatabaseAndState,
)

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def create_facility_processing_value_index(apps, schema_editor):
    """
    Create the api_facility_processing_value table and its delta triggers.

    Aggregating the facility_type and processing_type arrays of
    api_facilityindex on every request takes seconds over 2.5M rows, so the
    processing type typeahead reads case-normalized values and their location
    counts from this table instead. Exact submitted-variant counts choose a
    stable display value while each location counts only once per PostgreSQL
    lower-case identity. The counts follow api_facilityindex through triggers,
    which keeps them accurate without a scheduled rebuild. Junk sentinels such
    as the literal string 'null' are excluded here so they never reach
    suggestions, even for rows indexed before the sentinels were filtered out
    during indexing. See OSDEV-3189.
    """
    helper.run_sql_files([
        '0232_facility_processing_value_index.sql',
    ])


def populate_facility_processing_value_index(apps, schema_editor):
    """
    Fill the counts once the triggers are in place.

    This is a separate operation on a non-atomic migration so that the SHARE
    ROW EXCLUSIVE lock CREATE TRIGGER takes on api_facilityindex is released
    before the rebuild starts. That lock conflicts with the ROW EXCLUSIVE one
    every insert, update and delete needs, so holding it across the rebuild
    would block all indexing for the duration; the rebuild itself only reads
    api_facilityindex.
    """
    with connection.cursor() as cursor:
        cursor.execute('CALL recompute_facility_processing_values();')


def drop_facility_processing_value_index(apps, schema_editor):
    helper.run_sql_files([
        '0232_revert_facility_processing_value_index.sql',
    ])


def noop(apps, schema_editor):
    """The counts go away with the tables dropped by the reverse above."""


class Migration(Migration):

    # The trigger creation and the initial rebuild have to commit separately,
    # which a transaction around the whole migration would prevent.
    atomic = False

    dependencies = [
        ('api', '0231_index_facility_processing_raw_values'),
    ]

    operations = [
        SeparateDatabaseAndState(
            database_operations=[
                RunPython(
                    create_facility_processing_value_index,
                    drop_facility_processing_value_index,
                ),
            ],
            state_operations=[
                CreateModel(
                    name='FacilityProcessingValue',
                    fields=[
                        (
                            'pk',
                            models.CompositePrimaryKey(
                                'kind',
                                'identity',
                                blank=True,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        ('kind', models.TextField()),
                        ('identity', models.TextField()),
                        ('value', models.TextField()),
                        ('facility_count', models.IntegerField()),
                    ],
                    options={
                        'db_table': 'api_facility_processing_value',
                        'managed': False,
                    },
                ),
            ],
        ),
        RunPython(
            populate_facility_processing_value_index,
            noop,
        ),
    ]
