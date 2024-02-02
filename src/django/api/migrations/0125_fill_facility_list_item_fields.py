
from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def create_fill_fields_trigger(apps, schema_editor):
    helper.run_sql_files([
        '0125_fill_facility_list_item_fields.sql',
    ])


def revert_fill_fields_trigger(apps, schema_editor):
    helper.run_sql_files([
         '0125_fill_facility_list_item_fields_revert.sql',
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0124_inroduce_raw_json'),
    ]

    operations = [
        RunPython(create_fill_fields_trigger, revert_fill_fields_trigger),
    ]
