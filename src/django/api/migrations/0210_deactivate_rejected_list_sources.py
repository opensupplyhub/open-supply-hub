from django.db import migrations


def deactivate_rejected_list_sources(apps, schema_editor):
    """
    Rejected lists should always have their source deactivated. The reject()
    action does this at runtime, but a small number of lists were rejected
    before this logic was in place and still have is_active=True.
    """
    Source = apps.get_model('api', 'Source')

    Source.objects.filter(
        facility_list__status='REJECTED',
        is_active=True,
    ).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0209_clear_replaces_on_rejected_lists'),
    ]

    operations = [
        migrations.RunPython(
            deactivate_rejected_list_sources,
            migrations.RunPython.noop,
        ),
    ]
