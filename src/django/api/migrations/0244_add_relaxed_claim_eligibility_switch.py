from django.db import migrations

SWITCH_NAME = 'relaxed_claim_eligibility'


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

    dependencies = [
        ('api', '0243_add_claim_address_pin_move_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
