from django.db import migrations


SWITCH_NAME = 'polygons'


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
    Migration to introduce a switch gating the polygon admin.
    """

    dependencies = [
        ('api', '0224_create_polygon'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
