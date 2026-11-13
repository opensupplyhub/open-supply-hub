from django.db import migrations, models


# Serves the sector-filtered country map. Shading the map for one sector
# live means grouping all of api_facilityindex by country, which the GIN of
# 0272 brings down to 8ms for a narrow sector such as Aerospace but leaves
# at roughly 5.8s for a broad one such as Apparel, and broad is the common
# case.
#
# Measured on the same 2,537,087-row anonymized restore, the whole country
# x sector cube is 8,202 rows (224 countries x 256 sectors, sparse) and
# builds in one pass in 4.7s. Precomputing it daily alongside CountryStats
# turns the filtered map into a lookup, so how broad the sector is stops
# mattering. See OSDEV-3802.
class Migration(migrations.Migration):

    dependencies = [
        ('api', '0274_add_country_map_switch'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountrySectorStats',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('country_code', models.CharField(
                    help_text=(
                        'ISO 3166-1 alpha-2 code, matching FacilityIndex.'
                    ),
                    max_length=2,
                )),
                ('sector', models.CharField(
                    help_text=(
                        'One sector name exactly as it appears in '
                        'FacilityIndex.sector, which is a controlled '
                        'taxonomy and so is matched verbatim.'
                    ),
                    max_length=200,
                )),
                ('location_count', models.IntegerField(
                    help_text=(
                        'Open production locations in this country '
                        'reporting this sector. A location can report '
                        'several sectors, so these counts sum to more than '
                        'CountryStats.location_count.'
                    ),
                )),
                ('computed_at', models.DateTimeField(
                    help_text=(
                        'When this row was last rebuilt. Surfaced to readers '
                        'so a stalled rebuild is visible rather than '
                        'silently serving old numbers.'
                    ),
                )),
            ],
            options={
                'verbose_name': 'Country sector stats',
                'verbose_name_plural': 'Country sector stats',
                'ordering': ('sector', '-location_count'),
            },
        ),
        migrations.AddConstraint(
            model_name='countrysectorstats',
            constraint=models.UniqueConstraint(
                fields=('sector', 'country_code'),
                name='unique_country_sector_stats',
            ),
        ),
        migrations.AddIndex(
            model_name='countrysectorstats',
            index=models.Index(
                fields=['sector', 'country_code', 'location_count'],
                name='country_sector_stats_lookup',
            ),
        ),
    ]
