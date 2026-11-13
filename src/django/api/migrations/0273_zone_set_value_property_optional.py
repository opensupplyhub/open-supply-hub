from django.db import migrations, models


class Migration(migrations.Migration):
    """
    OSDEV-3659. `value_property` on api_zoneset becomes optional: a
    set that feeds an object-type partner field reads one feature
    property per key of the field's JSON schema, so it has no single
    value property (the admin form still requires one for a string
    field). Drops the NOT NULL constraint and nothing else; no row is
    changed. The AlterField on `Zone.value` only updates its help
    text to describe the object-field shape and emits no SQL. Runs
    under the same 5 s `lock_timeout` as 0271 because api_zoneset is
    read by the provider registry on every location page, so the
    ALTER TABLE fails fast rather than queue behind a reader. The
    reverse re-adds NOT NULL and fails if any object-field set has
    been saved with an empty value property; clear or re-link those
    sets first.
    """

    dependencies = [
        ('api', '0272_subdivide_existing_zones'),
    ]

    operations = [
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='zoneset',
            name='value_property',
            field=models.CharField(
                blank=True,
                null=True,
                max_length=200,
                help_text=(
                    'For a "string" partner field: the GeoJSON feature '
                    'property that supplies each zone\'s displayed value '
                    '(e.g. "bws_label"). Every feature in an upload must '
                    'carry it. Leave empty for an "object" field, which '
                    'reads one feature property per key of its JSON '
                    'schema instead.'
                ),
            ),
        ),
        migrations.AlterField(
            model_name='zone',
            name='value',
            field=models.JSONField(
                help_text=(
                    'The zone\'s value: {"label": <displayed value>, '
                    '"properties": {<every property of the source '
                    'feature>}}. For a set feeding an object field the '
                    'label is the first required schema property (or '
                    'empty) and the served values are read from '
                    '"properties" by schema key.'
                ),
            ),
        ),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
