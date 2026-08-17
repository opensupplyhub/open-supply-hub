import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0223_fix_sector_search_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='NamedPolygon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short, descriptive name for this boundary.', max_length=200)),
                ('description', models.TextField(help_text='Details about what this boundary represents and where it came from.')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='The boundary geometry in WGS 84 (EPSG:4326).', srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Named polygon',
                'verbose_name_plural': 'Named polygons',
            },
        ),
    ]
