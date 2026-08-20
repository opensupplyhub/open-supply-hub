import uuid

import django.contrib.gis.db.models.fields
from django.db import migrations, models

import api.models.polygon


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0223_fix_sector_search_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Polygon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the polygon.', unique=True)),
                ('name', models.CharField(help_text='A short machine-friendly identifier for this boundary, used to reference it from code. Letters, digits, and underscores only.', max_length=200, unique=True, validators=[api.models.polygon.variable_style_name_validator])),
                ('display_name', models.CharField(blank=True, help_text='Optional human-friendly name, for use if this boundary is ever displayed on OS Hub.', max_length=200)),
                ('description', models.TextField(help_text='Details about what this boundary represents and where it came from.')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='The boundary geometry in WGS 84 (EPSG:4326).', srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Polygon',
                'verbose_name_plural': 'Polygons',
            },
        ),
    ]
