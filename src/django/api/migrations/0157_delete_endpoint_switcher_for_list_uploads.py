# Generated by Django 3.2.17 on 2024-10-01 09:26

from django.db import migrations


class Migration(migrations.Migration):
    def create_list_upload_endpoint_switcher(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.create(name='use_old_upload_list_endpoint',
                              active=False)

    def delete_list_upload_endpoint_switcher(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.get(name='use_old_upload_list_endpoint').delete()

    dependencies = [
        ('api', '0156_introduce_list_level_parsing_errors'),
    ]

    operations = [
        migrations.RunPython(
            delete_list_upload_endpoint_switcher,
            create_list_upload_endpoint_switcher
        )
    ]
