from django.db import migrations


class Migration(migrations.Migration):
    '''
    This migration renames the facility_workers_count_new field
    to facility_workers_count.
    '''

    dependencies = [
        ('api', '0148_remove_facility_workers_count_field_from_facilityclaim'),
    ]

    operations = [
        migrations.RenameField(
            model_name='facilityclaim',
            old_name='facility_workers_count_new',
            new_name='facility_workers_count',
        ),
        migrations.RenameField(
            model_name='historicalfacilityclaim',
            old_name='facility_workers_count_new',
            new_name='facility_workers_count',
        ),
    ]
