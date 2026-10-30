"""Mark the FacilityClaim fields a submission may leave empty as form-optional.

Each column already accepts the empty value it is given at submission; without
blank=True the admin ModelForm rendered it as required (OSDEV-1065).
"""
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0260_isic_sector_crosswalk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_description',
            field=models.TextField(
                blank=True,
                help_text='A description of the facility',
                verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_location',
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True,
                help_text='The lat/lng point location of the facility',
                null=True,
                srid=4326,
                verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='facilityclaim',
            name='parent_company',
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text='The contributor parent company / supplier group '
                          'of thisfacility claim.',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='parent_company',
                to='api.contributor',
                verbose_name='contributor parent company / supplier group'),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_description',
            field=models.TextField(
                blank=True,
                help_text='A description of the facility',
                verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_location',
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True,
                help_text='The lat/lng point location of the facility',
                null=True,
                srid=4326,
                verbose_name='location'),
        ),
    ]
