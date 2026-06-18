from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_index_contributors(apps, schema_editor):
    helper.run_sql_files(['0213_index_contributors.sql'])


def revert_index_contributors(apps, schema_editor):
    helper.run_sql_files(['0130_index_contributors.sql'])


class Migration(Migration):

    dependencies = [
        ('api', '0212_add_moderation_pause_info_switch'),
    ]

    operations = [
        RunPython(update_index_contributors, revert_index_contributors),
    ]
