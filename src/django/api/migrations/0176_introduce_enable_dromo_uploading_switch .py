from django.db import migrations


class Migration(migrations.Migration):
    def create_enable_dromo_uploading_switch(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.create(name='enable_dromo_uploading',
                              active=False)

    def delete_enable_dromo_uploading_switch(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.get(name='enable_dromo_uploading').delete()

    dependencies = [
        ('api', '0175_increase_path_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_enable_dromo_uploading_switch,
            delete_enable_dromo_uploading_switch
        )
    ]
