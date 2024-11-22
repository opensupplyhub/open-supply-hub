# Generated by Django 3.2.17 on 2024-11-22 09:50

from django.db import migrations


def create_disable_list_uploading_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.create(name='disable_list_uploading', active=False)


def delete_disable_list_uploading_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get(name='disable_list_uploading').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0160_allow_null_parsing_errors_in_facilitylist'),
    ]

    operations = [
        migrations.RunPython(
            create_disable_list_uploading_switch,
            delete_disable_list_uploading_switch,)
    ]
