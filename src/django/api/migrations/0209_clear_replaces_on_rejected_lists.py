from django.db import migrations


def clear_replaces_on_rejected_lists(apps, schema_editor):
    """
    When a replacement list is rejected, the replaces FK should be cleared so
    the old list is no longer considered "replaced". The reject() action now
    does this at runtime, but lists rejected before that fix was deployed still
    have replaces_id set. Clear it retroactively.
    """
    FacilityList = apps.get_model('api', 'FacilityList')

    FacilityList.objects.filter(
        status='REJECTED',
        replaces__isnull=False,
    ).update(replaces=None)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0208_deactivate_replaced_list_sources'),
    ]

    operations = [
        migrations.RunPython(
            clear_replaces_on_rejected_lists,
            migrations.RunPython.noop,
        ),
    ]
