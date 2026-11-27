from django.db import migrations, models

NAME_HELP_TEXT = 'The name of the facility.'
ADDRESS_HELP_TEXT = 'The full street address of the facility.'
RAW_NAME_HELP_TEXT = 'The name of the facility taken from the raw data.'
RAW_ADDRESS_HELP_TEXT = 'The address of the facility taken from the raw data.'

# Facility tables first: api_facility writes reach api_historicalfacility
# and, through the index triggers, api_facilityindex, so taking the locks
# in that order matches the order writers take them.
TABLES = (
    'api_facility',
    'api_historicalfacility',
    'api_facilitylistitem',
    'api_facilitylistitemtemp',
    'api_facilityindex',
)


def alter_name_and_address_sql(length):
    return [
        f'''
        ALTER TABLE {table}
            ALTER COLUMN name TYPE varchar({length}),
            ALTER COLUMN address TYPE varchar({length});
        '''
        for table in TABLES
    ]


class Migration(migrations.Migration):
    """
    OSDEV-1085. Widens the name and address columns from 200 to 300
    characters on every table that stores the cleaned contributed value.
    ContriCleaner now checks the 200-character limit against the value the
    contributor submitted, and its cleanup can add characters afterwards
    (a space after each comma), so the stored value may exceed 200.
    """

    # Raising a varchar limit only updates the catalog: no table rewrite,
    # and the facility index's name/address indexes are kept. Each ALTER
    # still takes an ACCESS EXCLUSIVE lock, and these are the largest,
    # busiest tables. Non-atomic (like 0237) so each table's lock is
    # released as soon as its ALTER commits: in one transaction every lock
    # would be held until the last table is altered, blocking all reads of
    # the tables already done while a later ALTER waits. The lock_timeout
    # makes an ALTER fail fast instead of queueing behind a long-running
    # query (and every later query queueing behind it). Widening is
    # idempotent, so after a timeout the recovery is rerunning migrate.
    atomic = False

    dependencies = [
        ('api', '0264_qualify_facility_processing_search_functions'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "SET lock_timeout = '5s';",
                        *alter_name_and_address_sql(300),
                        'RESET lock_timeout;',
                    ],
                    # Shrinking rescans each table and fails if any stored
                    # value is longer than 200 characters.
                    reverse_sql=[
                        "SET lock_timeout = '5s';",
                        *reversed(alter_name_and_address_sql(200)),
                        'RESET lock_timeout;',
                    ],
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='facility',
                    name='name',
                    field=models.CharField(
                        help_text=NAME_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facility',
                    name='address',
                    field=models.CharField(
                        help_text=ADDRESS_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='historicalfacility',
                    name='name',
                    field=models.CharField(
                        help_text=NAME_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='historicalfacility',
                    name='address',
                    field=models.CharField(
                        help_text=ADDRESS_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilitylistitem',
                    name='name',
                    field=models.CharField(
                        help_text=RAW_NAME_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilitylistitem',
                    name='address',
                    field=models.CharField(
                        help_text=RAW_ADDRESS_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilitylistitemtemp',
                    name='name',
                    field=models.CharField(
                        help_text=RAW_NAME_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilitylistitemtemp',
                    name='address',
                    field=models.CharField(
                        help_text=RAW_ADDRESS_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilityindex',
                    name='name',
                    field=models.CharField(
                        db_index=True,
                        help_text=NAME_HELP_TEXT,
                        max_length=300,
                    ),
                ),
                migrations.AlterField(
                    model_name='facilityindex',
                    name='address',
                    field=models.CharField(
                        db_index=True,
                        help_text=ADDRESS_HELP_TEXT,
                        max_length=300,
                    ),
                ),
            ],
        ),
    ]
