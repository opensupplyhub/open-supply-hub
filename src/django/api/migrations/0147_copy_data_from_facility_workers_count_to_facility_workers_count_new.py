from django.db import migrations


def copy_integer_to_char(apps, schema_editor):
    FacilityClaim = apps.get_model('your_app_name', 'FacilityClaim')
    for instance in FacilityClaim.objects.all():
        if instance.facility_workers_count:
            instance.facility_workers_count_new = str(
                instance.facility_workers_count
            )
            instance.save()


class Migration(migrations.Migration):
    '''
    This migration copies the data from the facility_workers_count field
    to the facility_workers_count_new field.
    '''

    dependencies = [
        ('api', '0146_add_facility_workers_count_new_field_to_facilityclaim'),
    ]

    operations = [
        migrations.RunPython(copy_integer_to_char),
    ]
