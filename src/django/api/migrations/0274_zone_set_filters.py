from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds `filters` to api_zoneset: an optional JSON setting that
    limits a zone set to the locations matching it (sector, country,
    product type and the other polygon filter fields). The default is
    an empty object, which means "no filters", so every existing set
    behaves exactly as before and no row needs backfilling. Adds one
    column and nothing else. Runs under the same 5 s `lock_timeout`
    as 0273 because api_zoneset is read by the provider registry on
    every location page, so the ALTER TABLE fails fast rather than
    queue behind a reader. The reverse drops the column and with it
    any filters set since.
    """

    dependencies = [
        ('api', '0273_zone_set_value_property_optional'),
    ]

    operations = [
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='zoneset',
            name='filters',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Optional: only show this dataset on locations that '
                    'match, e.g. {"sector": ["Mining"]} or {"country": '
                    '["KH"], "product_type": ["sugarcane"]}. Allowed '
                    'keys: country, sector, facility_type, '
                    'processing_type, product_type, parent_company (the '
                    'same ones polygon filters use). Within one key the '
                    'values are alternatives; across keys a location '
                    'must match all. Sector and the other names must '
                    'be spelled exactly as they appear on locations; '
                    'product types are not case sensitive. Leave empty '
                    'to show the dataset on every location inside a '
                    'zone.'
                ),
            ),
        ),
    ]
