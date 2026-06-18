from django.db import connection
from django.db.migrations import Migration, RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_is_from_created_from_to_name_address_index(apps, schema_editor):
    # Adds an `is_from_created_from` flag to the facility name/address index
    # functions so the promoted (created_from) contribution can be attributed
    # as the source of the canonical name/address even when several
    # contributions share the same value. See OSDEV-2197.
    helper.run_sql_files([
        '0213_index_facility_names.sql',
        '0213_index_facility_addresses.sql',
    ])


def revert_is_from_created_from_to_name_address_index(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_facility_names.sql',
        '0130_index_facility_addresses.sql',
    ])


class Migration(Migration):
    dependencies = [('api', '0212_add_moderation_pause_info_switch')]
    operations = [
        RunPython(
            add_is_from_created_from_to_name_address_index,
            revert_is_from_created_from_to_name_address_index,
        )
    ]
