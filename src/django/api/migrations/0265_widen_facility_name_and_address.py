from django.db import migrations, models

NAME_HELP_TEXT = 'The name of the facility.'
ADDRESS_HELP_TEXT = 'The full street address of the facility.'
RAW_NAME_HELP_TEXT = 'The name of the facility taken from the raw data.'
RAW_ADDRESS_HELP_TEXT = 'The address of the facility taken from the raw data.'


class Migration(migrations.Migration):
    """
    OSDEV-1085. Widens the name and address columns from 200 to 300
    characters on every table that stores the cleaned contributed value.
    ContriCleaner now checks the 200-character limit against the value the
    contributor submitted, and its cleanup can add characters afterwards
    (a space after each comma), so the stored value may exceed 200.

    Raising a varchar limit in PostgreSQL only updates the catalog: the
    tables are not rewritten and the facility index's name/address
    indexes are kept as they are.
    """

    dependencies = [
        ('api', '0264_qualify_facility_processing_search_functions'),
    ]

    operations = [
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
    ]
