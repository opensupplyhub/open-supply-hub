"""Mark FacilityClaim location and parent company as form-optional.

Both columns were already nullable; without blank=True Django's admin
ModelForm rendered them as required and blocked every save (OSDEV-1065).
"""
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0259_facility_claim_invite'),
    ]

    operations = [
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
            name='facility_location',
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True,
                help_text='The lat/lng point location of the facility',
                null=True,
                srid=4326,
                verbose_name='location'),
        ),
    ]
