from django.contrib.postgres.fields import ArrayField
from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.isic_taxonomy.crosswalk import (
    load_crosswalk_rows,
    replace_crosswalk_entries,
)
from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def seed_crosswalk(apps, schema_editor):
    replace_crosswalk_entries(
        apps.get_model('api', 'IsicCrosswalkEntry'),
        load_crosswalk_rows(),
    )


def clear_crosswalk(apps, schema_editor):
    apps.get_model('api', 'IsicCrosswalkEntry').objects.all().delete()


def add_isic_mapped_indexing(apps, schema_editor):
    helper.run_sql_files(['0256_isic_mapped_from_taxonomy.sql'])


def remove_isic_mapped_indexing(apps, schema_editor):
    helper.run_sql_files(['0256_revert_isic_mapped_from_taxonomy.sql'])


class Migration(migrations.Migration):
    """
    OSDEV-3382. Adds the OS Hub to ISIC Rev 4 crosswalk table, seeded from
    api/isic_taxonomy/data/os_hub_to_isic4_crosswalk.csv, and the
    isic_mapped_* columns of api_facilityindex with the triggers that keep
    them current. Existing rows are filled by the post-deploy
    `backfill_facility_index --fields isic_4_mapped`, not here, so the
    migration does not rewrite the whole index table.
    """

    dependencies = [
        ('api', '0255_index_isic_search'),
    ]

    operations = [
        # Guards the ALTERs on api_facilityindex, as in 0254 and 0251.
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name='IsicCrosswalkEntry',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('facility_type', models.CharField(max_length=200)),
                ('processing_type', models.CharField(
                    blank=True, max_length=200,
                )),
                ('isic_section', models.CharField(
                    blank=True, max_length=1,
                )),
                ('isic_section_title', models.CharField(
                    blank=True, max_length=300,
                )),
                ('isic_division', models.CharField(
                    blank=True, max_length=2,
                )),
                ('isic_division_title', models.CharField(
                    blank=True, max_length=300,
                )),
                ('isic_group', models.CharField(
                    blank=True, max_length=3,
                )),
                ('isic_group_title', models.CharField(
                    blank=True, max_length=300,
                )),
                ('isic_class', models.CharField(
                    blank=True, max_length=4,
                )),
                ('isic_class_title', models.CharField(
                    blank=True, max_length=300,
                )),
            ],
        ),
        RunPython(seed_crosswalk, clear_crosswalk),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_mapped_section',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 4 section codes mapped from the facility '
                        'and processing type through the crosswalk.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_mapped_division',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 4 division codes mapped from the facility '
                        'and processing type through the crosswalk.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_mapped_group',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 4 group codes mapped from the facility '
                        'and processing type through the crosswalk.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_mapped_class',
            field=ArrayField(
                base_field=models.CharField(
                    help_text=(
                        'ISIC Rev 4 class codes mapped from the facility '
                        'and processing type through the crosswalk.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        RunPython(add_isic_mapped_indexing, remove_isic_mapped_indexing),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
