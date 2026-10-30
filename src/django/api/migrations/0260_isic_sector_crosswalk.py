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


def clear_sector_rows(apps, schema_editor):
    apps.get_model('api', 'IsicCrosswalkEntry').objects.exclude(
        sector='',
    ).delete()


def add_sector_mapping(apps, schema_editor):
    helper.run_sql_files(['0260_isic_mapped_from_sector.sql'])


def remove_sector_mapping(apps, schema_editor):
    helper.run_sql_files([
        '0260_revert_isic_mapped_from_sector.sql',
        '0256_isic_mapped_from_taxonomy.sql',
    ])


class Migration(migrations.Migration):
    """
    OSDEV-3382. Adds the Sector part of the OS Hub to ISIC Rev 4 crosswalk,
    seeded from api/isic_taxonomy/data/os_hub_sector_to_isic4_crosswalk.csv,
    and maps each location's sectors into the isic_mapped_* columns
    alongside its Facility Type / Processing Type. Existing rows are filled
    by the post-deploy `backfill_facility_index --fields isic_4_mapped`, as
    in 0256.
    """

    dependencies = [
        ('api', '0259_facility_claim_invite'),
    ]

    operations = [
        # Guards the trigger changes on api_facilityindex, as in 0256.
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='isiccrosswalkentry',
            name='sector',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='isiccrosswalkentry',
            name='facility_type',
            field=models.CharField(blank=True, max_length=200),
        ),
        RunPython(seed_crosswalk, clear_sector_rows),
        RunPython(add_sector_mapping, remove_sector_mapping),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
