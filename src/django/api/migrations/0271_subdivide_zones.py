from django.db import migrations, models


class Migration(migrations.Migration):
    """
    OSDEV-3744, schema step. Zones are stored as pieces of a bounded
    vertex count so a dissolved layer (few features, very many
    vertices) costs the point-in-polygon test in the indexing trigger
    and the zone_set_ids recompute no more than a layer of many small
    features (see api/helpers/zone_subdivision.py).

    Adds `piece_index` to api_zone and replaces the one-row-per-feature
    unique constraint with one over (zone_set, feature_index,
    piece_index). Every existing row gets piece_index 0; 0272 then
    re-cuts the rows in a transaction of its own. The two are kept
    apart on purpose: the ALTER TABLEs here take an ACCESS EXCLUSIVE
    lock on api_zone that is held until this migration commits, and
    api_zone is read by the facility indexing trigger on every facility
    save, by every location page (resolve_zone) and for minutes at a
    time by the zone_set_ids recompute Batch job. Doing the row rewrite
    here would hold every one of those readers for as long as it takes;
    on its own it takes only row locks, which no reader waits for.

    The reverse restores the old constraint and drops the column; 0272's
    reverse has merged each feature's pieces back into one row by then.
    """

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
    ]

    operations = [
        # The ALTERs below must not queue behind a reader of api_zone
        # and stall every query that arrives meanwhile. SET LOCAL lasts
        # to the end of the migration transaction; the RunSQL at the
        # end does the same when migrating backwards (as in 0267).
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
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
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
