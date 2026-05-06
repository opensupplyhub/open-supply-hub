from django.db import migrations


def deactivate_replaced_list_sources(apps, schema_editor):
    """
    For all FacilityLists that were replaced by an already-approved list,
    set their Source.is_active to False.
    """
    Source = apps.get_model('api', 'Source')

    Source.objects.filter(
        facility_list__replaced_by__status='APPROVED',
        is_active=True,
    ).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0207_add_energy_and_throughput_to_index_approved_claim'),
    ]

    operations = [
        migrations.RunPython(
            deactivate_replaced_list_sources,
            migrations.RunPython.noop,
        ),
    ]
