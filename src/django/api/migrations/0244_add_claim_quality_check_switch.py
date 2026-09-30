from django.db import migrations


SWITCH_NAME = 'claim_quality_check'


def create_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': True},
    )


def delete_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch that controls the LLM-backed quality
    check on the name and address a claimant asserts (OSDEV-3489). The
    check also requires enable_claim_name_address_edit (inactive, from
    migration 0241), so this one is created active: it is the kill
    switch for the model call alone, and deploying it changes nothing.
    """

    dependencies = [
        ('api', '0243_add_claim_address_pin_move_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
