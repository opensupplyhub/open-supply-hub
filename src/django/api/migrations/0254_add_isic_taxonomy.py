from django.contrib.postgres.fields import ArrayField
from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

SWITCH_NAME = 'enable_isic_taxonomy'


def create_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


def add_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0254_extract_isic_code.sql',
        '0254_index_isic_4.sql',
    ])


def revert_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0254_revert_index_isic_4.sql',
    ])


def update_indexing_procedures(apps, schema_editor):
    helper.run_sql_files([
        '0254_index_facilities_isic.sql',
        '0254_extended_field_indexing_isic.sql',
        '0254_isic_dependent_triggers.sql',
    ])


def revert_indexing_procedures(apps, schema_editor):
    # Each file re-creates the definitions this migration replaced.
    helper.run_sql_files([
        '0250_index_facilities_exclude_candidates.sql',
        '0254_revert_extended_field_indexing_isic.sql',
        '0235_add_taxonomy_columns_to_dependent_triggers.sql',
        '0236_add_taxonomy_columns_to_claim_trigger.sql',
    ])


class Migration(migrations.Migration):
    """
    Adds the ISIC Rev 4 and Rev 5 columns to api_facilityindex and the
    functions and procedure changes that fill them from the isic_4 and
    isic_5 ExtendedFields.

    Also adds the `enable_isic_taxonomy` switch, created inactive. The
    taxonomy and counts views (and the profile's mapped values) check it
    before reading the new columns or the crosswalk table: `migrate` runs
    in post-deploy, after the new image is live (as in 0247). It hides
    ISIC on the site but does not gate the `isic_4` / `isic_5` search
    filters. It cannot cover the new api_facilityindex
    columns, which every FacilityIndex query selects: as with 0171, search
    and profiles can fail until this migration has run.
    """

    dependencies = [
        ('api', '0253_add_earth_genome_candidates_switch'),
    ]

    operations = [
        # api_facilityindex is read by long-running queries (downloads,
        # tiles); the ALTERs below must not queue behind them and stall
        # every query that arrives meanwhile. SET LOCAL lasts to the end of
        # the migration transaction; the RunSQL at the end does the same
        # when migrating backwards (as in 0251).
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_class',
            field=ArrayField(
                base_field=models.CharField(
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
        migrations.AddField(
            model_name='facilityindex',
            name='isic5_class',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 5 class codes from isic_5 ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic5_division',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 5 division codes from isic_5 ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic5_group',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 5 group codes from isic_5 ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic5_section',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 5 section codes from isic_5 ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        RunPython(add_isic_indexing_functions, revert_isic_indexing_functions),
        RunPython(update_indexing_procedures, revert_indexing_procedures),
        RunPython(create_switch, delete_switch),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
