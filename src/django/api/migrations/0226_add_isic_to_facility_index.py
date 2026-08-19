from django.contrib.postgres.fields import ArrayField
from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0224_extract_isic_code.sql',
        '0224_index_isic_4.sql',
    ])


def revert_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0224_revert_index_isic_4.sql',
    ])


def update_indexing_procedures(apps, schema_editor):
    helper.run_sql_files([
        '0224_index_facilities.sql',
        '0224_index_facilities_by.sql',
    ])


def revert_indexing_procedures(apps, schema_editor):
    helper.run_sql_files([
        '0171_index_facilities.sql',
        '0171_index_facilities_by.sql',
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0225_add_is_anonymized_to_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityindex',
            name='isic_class',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 class codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_division',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 division codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_group',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 group codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_section',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 section codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        RunPython(add_isic_indexing_functions, revert_isic_indexing_functions),
        RunPython(update_indexing_procedures, revert_indexing_procedures),
    ]
