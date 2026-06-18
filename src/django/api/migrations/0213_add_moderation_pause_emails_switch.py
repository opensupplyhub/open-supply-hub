from django.db import migrations


SWITCH_NAME = 'enable_moderation_pause_emails'


def create_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch for the moderation pause confirmation emails.
    """

    dependencies = [
        ('api', '0212_add_moderation_pause_info_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
