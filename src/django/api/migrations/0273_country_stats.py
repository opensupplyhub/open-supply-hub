import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0272_index_sector_search'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryStats',
            fields=[
                ('country_code', models.CharField(
                    help_text=(
                        'ISO 3166-1 alpha-2 code, matching FacilityIndex.'
                    ),
                    max_length=2,
                    primary_key=True,
                    serialize=False,
                )),
                ('location_count', models.IntegerField(
                    help_text=(
                        'Open production locations in this country. Excludes '
                        'locations explicitly marked closed; note is_closed '
                        'is null for almost every row, so the filter is "is '
                        'not true" rather than "not".'
                    ),
                )),
                ('sectors', models.JSONField(
                    default=list,
                    help_text=(
                        'Sectors represented, as [{"sector": str, "count": '
                        'int}] sorted by count descending. A location can '
                        'report several sectors, so these counts sum to more '
                        'than location_count.'
                    ),
                )),
                ('partner_fields',
                 django.contrib.postgres.fields.ArrayField(
                     base_field=models.CharField(max_length=200),
                     default=list,
                     help_text=(
                         'Names of the Spotlight partner fields with data '
                         'for at least one location in this country. '
                         'Presence only, deliberately: the product question '
                         'is whether we hold the data, not how much.'
                     ),
                     size=None,
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
                'verbose_name': 'Country stats',
                'verbose_name_plural': 'Country stats',
                'ordering': ('-location_count',),
            },
        ),
    ]
