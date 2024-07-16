# Generated by Django 3.2.4 on 2023-10-25 11:45

from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def replace_number_of_workers_functions(apps, schema_editor):
    helper.run_sql_files([
        '0151_index_number_of_workers.sql',
    ])


def revert_replace_number_of_workers_functions(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_number_of_workers.sql',
    ])


class Migration(Migration):
    dependencies = [('api', '0150_introduce_function_formatting_number_to_percent')]
    operations = [
        RunPython(replace_number_of_workers_functions,
                  revert_replace_number_of_workers_functions)
    ]
