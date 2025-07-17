from django.db import migrations


def create_enable_dromo_uploading_switch(apps, schema_editor):
    switch = apps.get_model('waffle', 'Switch')
    switch.objects.create(name='enable_dromo_uploading', active=False)


def delete_enable_dromo_uploading_switch(apps, schema_editor):
    switch = apps.get_model('waffle', 'Switch')
    switch.objects.get(name='enable_dromo_uploading').delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch for enabling Dromo uploading.
    """

    dependencies = [
        ('api', '0175_increase_path_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_enable_dromo_uploading_switch,
            delete_enable_dromo_uploading_switch,
        )
    ]
