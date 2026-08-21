from django.db import migrations


SWITCH_NAME = 'india_labour_line_helpline'


def create_switch(apps, schema_editor):
    """Create the switch, off by default."""
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    """Remove the switch when the migration is rolled back."""
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch gating the India Labour Line
    helpline partner field (provider, spotlight, and search filter).
    """

    dependencies = [
        ('api', '0228_add_polygons_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
