# Generated by Django 3.2.17 on 2025-04-25 14:56

from django.db import migrations


class Migration(migrations.Migration):
    def create_block_location_downloads_switch(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.create(name='block_location_downloads',
                              active=False)

    def delete_block_location_downloads_switch(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.get(name='block_location_downloads').delete()

    dependencies = [
        ('api', '0167_add_moderationevent_action_reason_text_fields'),
    ]

    operations = [
        migrations.RunPython(
            create_block_location_downloads_switch,
            delete_block_location_downloads_switch
        )
    ]
