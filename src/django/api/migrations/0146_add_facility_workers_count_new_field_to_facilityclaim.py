from django.db import migrations, models


class Migration(migrations.Migration):
    '''
    This migration adds the facility_workers_count_new field
    to the FacilityClaim model.
    '''

    dependencies = [
        ('api', '0145_new_functions_for_clean_facilitylistitems_command'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaim',
            name='facility_workers_count_new',
            field=models.CharField(
                blank=True,
                help_text='The editable facility workers count for this claim',
                max_length=200,
                null=True,
                verbose_name='facility workers count',
            ),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='facility_workers_count_new',
            field=models.CharField(
                blank=True,
                help_text='The editable facility workers count for this claim',
                max_length=200,
                null=True,
                verbose_name='facility workers count',
            ),
        ),
    ]
