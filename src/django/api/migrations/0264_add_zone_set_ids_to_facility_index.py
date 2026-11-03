from django.contrib.postgres.fields import ArrayField
from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_zone_set_ids_indexing(apps, schema_editor):
    helper.run_sql_files([
        '0264_index_zone_set_ids.sql',
        '0264_index_facilities_zone_set_ids.sql',
    ])


def revert_zone_set_ids_indexing(apps, schema_editor):
    # Restores the procedure definitions this migration replaced, then
    # drops the function they stopped referencing.
    helper.run_sql_files([
        '0254_index_facilities_isic.sql',
        '0264_revert_index_zone_set_ids.sql',
    ])


class Migration(migrations.Migration):
    """
    OSDEV-3743. Adds `zone_set_ids` to api_facilityindex: the ids of the
    zone sets with a zone covering the row's location, so a zone-set
    Spotlight partner search runs from an array column (and, after 0265,
    a GIN index) instead of a point-in-polygon test over the whole table.

    Adds the index_zone_set_ids(location) function and re-creates
    index_facilities_by / index_facilities (from 0254) to fill the column,
    so every facility save keeps it current. Existing rows get the empty
    default here and are filled by the post-deploy backfill
    (`backfill_facility_index --fields zone_set_ids`).

    As with 0171 and 0254, the new column is selected by every
    FacilityIndex query, so search and profiles can fail between the new
    image going live and this migration finishing.
    """

    dependencies = [
        ('api', '0263_seed_claim_profile_options'),
    ]

    operations = [
        # api_facilityindex is read by long-running queries (downloads,
        # tiles); the ALTER below must not queue behind them and stall
        # every query that arrives meanwhile. SET LOCAL lasts to the end
        # of the migration transaction; the RunSQL at the end does the
        # same when migrating backwards (as in 0254).
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='zone_set_ids',
            field=ArrayField(
                base_field=models.IntegerField(
                    help_text=(
                        'The id of a zone set with a zone covering the '
                        'location.'
                    ),
                ),
                default=list,
                help_text=(
                    'The ids of every zone set (active or not) with a '
                    'zone covering the location, kept current by '
                    'index_facilities_by. Search resolves the active '
                    'sets to look for; see '
                    'get_active_zone_sets_for_fields.'
                ),
                size=None,
            ),
        ),
        RunPython(add_zone_set_ids_indexing, revert_zone_set_ids_indexing),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
