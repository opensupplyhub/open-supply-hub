from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def subdivide_existing_zones(apps, schema_editor):
    helper.run_sql_files(['0269_subdivide_zones.sql'])


def merge_pieces_back(apps, schema_editor):
    helper.run_sql_files(['0269_revert_subdivide_zones.sql'])


class Migration(migrations.Migration):
    """
    OSDEV-3744. Zones are stored as pieces of a bounded vertex count so
    a dissolved layer (few features, very many vertices) costs the
    point-in-polygon test in the indexing trigger and the zone_set_ids
    recompute no more than a layer of many small features.

    Adds `piece_index` to api_zone, replaces the one-row-per-feature
    unique constraint with one over (zone_set, feature_index,
    piece_index), and re-cuts every existing zone in place with the
    same `ST_Subdivide` budget `ZoneSet.replace_zones` applies to new
    uploads, so no set needs re-uploading. Coverage and labels are
    unchanged (every piece carries its feature's value and
    feature_index), so `FacilityIndex.zone_set_ids` needs no recompute.

    The reverse merges each feature's pieces back into one row before
    restoring the old constraint; see 0269_revert_subdivide_zones.sql
    for the floating-point caveat.
    """

    dependencies = [
        ('api', '0268_index_zone_set_ids_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='piece_index',
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    'Position of this piece within its source feature '
                    '(0-based). Large features are cut into pieces of a '
                    'bounded vertex count at upload; every piece carries '
                    "the feature's value."
                ),
            ),
        ),
        migrations.AlterModelOptions(
            name='zone',
            options={
                'ordering': ('zone_set', 'feature_index', 'piece_index'),
                'verbose_name': 'Zone',
                'verbose_name_plural': 'Zones',
            },
        ),
        migrations.RemoveConstraint(
            model_name='zone',
            name='zone_unique_feature_index_per_set',
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.UniqueConstraint(
                fields=('zone_set', 'feature_index', 'piece_index'),
                name='zone_unique_piece_per_feature_per_set',
            ),
        ),
        RunPython(subdivide_existing_zones, merge_pieces_back),
    ]
