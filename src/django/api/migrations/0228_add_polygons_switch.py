from django.db import migrations


SWITCH_NAME = 'polygons'


def create_switch(apps, schema_editor):
    """Create the switch, off by default."""
    switch_model = apps.get_model('waffle', 'Switch')
    switch_model.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    """Remove the switch when the migration is rolled back."""
    switch_model = apps.get_model('waffle', 'Switch')
    switch_model.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch gating the polygon admin.
    """

    dependencies = [
        ('api', '0227_create_polygon'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
