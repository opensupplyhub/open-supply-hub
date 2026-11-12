from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_organization_guard(apps, schema_editor):
    helper.run_sql_files(['0271_skip_indexing_on_organization_stamp.sql'])


def remove_organization_guard(apps, schema_editor):
    helper.run_sql_files(
        ['0271_revert_skip_indexing_on_organization_stamp.sql']
    )


class Migration(Migration):
    """
    Stops the api_source and api_facilityclaim indexing triggers from
    re-indexing production locations when the only column an UPDATE
    changed is organization_id. The facility index holds nothing about
    organizations, and attributing a member's earlier contributions to
    their organization updates many rows at once. Every other insert
    and update is indexed exactly as before.
    """

    dependencies = [
        ('api', '0270_index_organization_columns'),
    ]

    operations = [
        RunPython(add_organization_guard, remove_organization_guard)
    ]
