from django.db import connection, migrations, models

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

NEW_SQL_FILES = [
    '0225_index_contributors.sql',
    '0225_index_created_from_info.sql',
    '0225_index_contributors_id.sql',
    '0225_index_item_sectors.sql',
    '0225_index_facility_names.sql',
    '0225_index_facility_addresses.sql',
    '0225_index_facility_list_items.sql',
    '0225_index_extended_fields.sql',
]

PREVIOUS_SQL_FILES = [
    '0217_index_contributors.sql',
    '0130_index_created_from_info.sql',
    '0130_index_contributors_id.sql',
    '0120_index_item_sectors.sql',
    '0215_index_facility_names.sql',
    '0215_index_facility_addresses.sql',
    '0130_index_facility_list_items.sql',
    '0130_index_extended_fields.sql',
]


def apply_is_anonymized_to_index_functions(apps, schema_editor):
    # Excludes anonymized sources from contributor attribution
    # (should_display_associations flags and the contributor search index)
    # while keeping their contributed data indexed. See OSDEV-3142.
    helper.run_sql_files(NEW_SQL_FILES)


def revert_is_anonymized_from_index_functions(apps, schema_editor):
    helper.run_sql_files(PREVIOUS_SQL_FILES)


class Migration(migrations.Migration):
    """
    Adds the Source.is_anonymized flag and teaches the facility index
    functions to hide contributor attribution (but not contributed data)
    for anonymized sources.
    """

    dependencies = [
        ('api', '0224_add_anonymize_slc_sources_switch'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='is_anonymized',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'True if the data from this source should be shown '
                    'without identifying the contributor. Unlike is_public, '
                    'the contributed data (names, addresses, sectors, '
                    'extended fields) remains visible.'
                ),
            ),
        ),
        migrations.RunPython(
            apply_is_anonymized_to_index_functions,
            revert_is_anonymized_from_index_functions,
        ),
    ]
