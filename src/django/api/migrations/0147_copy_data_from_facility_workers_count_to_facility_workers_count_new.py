from django.db import migrations

from api.models.facility.facility_claim import FacilityClaim


def copy_integer_to_char():
    for instance in FacilityClaim.objects.all():
        instance.original_field_char = str(instance.original_field)
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
