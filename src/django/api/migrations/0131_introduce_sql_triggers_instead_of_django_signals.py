# Generated by Django 3.2.4 on 2023-11-02 10:49

from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def introduce_sql_triggers(apps, schema_editor):
    """
    Introduce SQL triggers instead of Django signals.
    """
    helper.run_sql_files(['0131_create_table_triggers.sql'])


def revert_sql_triggers(apps, schema_editor):
    helper.run_sql_files(['0131_revert_the_creation_of_table_triggers.sql'])


class Migration(Migration):
    dependencies = [
        ('api',
         '0130_introduce_separate_data_gathering_functions_for_the_index_table_columns')
        ]

    operations = [
        RunPython(introduce_sql_triggers, revert_sql_triggers)
    ]
