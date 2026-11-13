from django.db import migrations, models


# Hand-written. The column is unchanged: the country card's sector list now
# holds sector group names instead of raw sector names, and this only brings
# the help text into line with what `compute_country_stats` writes. No data
# migration, because the next scheduled rebuild replaces every row anyway.
# See OSDEV-3802.
class Migration(migrations.Migration):

    dependencies = [
        ('api', '0273_country_sector_stats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrystats',
            name='sectors',
            field=models.JSONField(
                default=list,
                help_text=(
                    'Sector groups represented, as [{"sector": str, '
                    '"count": int}] sorted by count descending. The key '
                    'stays "sector" because the card reads it that way; the '
                    'value is a sector group name, rolled up from the raw '
                    'sectors because the raw list runs to 141 '
                    'near-duplicate names for a country such as India. Each '
                    'count is distinct locations reporting any sector in '
                    'that group, so a location naming two sectors in one '
                    'group counts once. A sector can belong to several '
                    'groups, so these counts still sum to more than '
                    'location_count. See OSDEV-3802.'
                ),
            ),
        ),
    ]
