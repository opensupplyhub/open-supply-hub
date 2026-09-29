from django.db import migrations


SWITCH_NAME = 'enable_claim_address_pin_move'


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
    Switch that lets an approved claim's changed address move the
    production location pin (geocoded, with distance and precision
    guards). Created inactive so the change ships dark and can be turned
    off without a deploy, since it alters live location data; while off,
    the claim contribution is placed at the current pin as in OSDEV-3405.
    See OSDEV-3406.
    """

    dependencies = [
        ('api', '0242_claim_contribution_events'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
