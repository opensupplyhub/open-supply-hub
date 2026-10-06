import uuid

import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add the zone ingestor models (OSDEV-3551): ZoneSet, a zoned
    geospatial dataset linked to one Spotlight partner field, and Zone,
    one polygon of that set carrying a value. The MultiPolygonField
    gets PostGIS's default GiST spatial index.
    """

    dependencies = [
        ('api', '0245_add_claim_quality_check_switch'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoneSet',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID',
                )),
                ('uuid', models.UUIDField(
                    default=uuid.uuid4, editable=False,
                    help_text='Unique identifier for the zone set.',
                    unique=True,
                )),
                ('name', models.CharField(
                    help_text=(
                        'A short machine-friendly identifier for this '
                        'dataset (e.g. "aqueduct_baseline_water_stress"). '
                        'Letters, digits, and underscores only.'
                    ),
                    max_length=200, unique=True,
                    validators=[django.core.validators.RegexValidator(
                        message=(
                            'Name must contain only letters, digits, and '
                            'underscores, and must not start with a digit '
                            '(e.g. "national_capital_territory_of_delhi").'
                        ),
                        regex='^[a-zA-Z_][a-zA-Z0-9_]*$',
                    )],
                )),
                ('description', models.TextField(
                    help_text=(
                        'Details about what this dataset represents, where '
                        'it came from, and how the file was prepared.'
                    ),
                )),
                ('value_property', models.CharField(
                    help_text=(
                        'The GeoJSON feature property that supplies each '
                        'zone\'s displayed value (e.g. "bws_label"). Every '
                        'feature in an upload must carry it.'
                    ),
                    max_length=200,
                )),
                ('active', models.BooleanField(
                    default=True,
                    help_text=(
                        'Inactive zone sets serve no values. Use this to '
                        'retire a dataset without deleting its zones.'
                    ),
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('partner_field', models.OneToOneField(
                    blank=True, null=True,
                    help_text=(
                        'The Spotlight partner field this dataset feeds. '
                        "The field's label is the displayed title, its "
                        'source_by text is the attribution line, and its '
                        'base URL / display text is the source link. The '
                        'dataset serves nothing until a field is linked and '
                        'a contributor holds that field. Deleting a field '
                        'that a zone set points at is blocked.'
                    ),
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='zone_set', to='api.partnerfield',
                )),
            ],
            options={
                'verbose_name': 'Zone set',
                'verbose_name_plural': 'Zone sets',
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID',
                )),
                ('feature_index', models.PositiveIntegerField(
                    help_text=(
                        'Position of the source feature in the uploaded '
                        'file (0-based). When zones in a set overlap, the '
                        'lowest index wins.'
                    ),
                )),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(
                    help_text='The zone geometry in WGS 84 (EPSG:4326).',
                    srid=4326,
                )),
                ('value', models.JSONField(
                    help_text=(
                        'The zone\'s value: {"label": <displayed value>, '
                        '"properties": {<every property of the source '
                        'feature>}}.'
                    ),
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('zone_set', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='zones', to='api.zoneset',
                )),
            ],
            options={
                'verbose_name': 'Zone',
                'verbose_name_plural': 'Zones',
                'ordering': ('zone_set', 'feature_index'),
            },
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.UniqueConstraint(
                fields=('zone_set', 'feature_index'),
                name='zone_unique_feature_index_per_set',
            ),
        ),
    ]
