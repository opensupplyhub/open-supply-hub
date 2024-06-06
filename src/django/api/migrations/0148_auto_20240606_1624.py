from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            'api',
            '0147_copy_data_from_facility_workers_count_to_facility_workers_count_new',
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facilityclaim',
            name='facility_workers_count',
        ),
        migrations.RemoveField(
            model_name='historicalfacilityclaim',
            name='facility_workers_count',
        ),
    ]
