from django.db import migrations


SWITCH_NAME = 'enable_production_location_page'


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
    Migration to introduce a switch for the production location page routing.
    """

    dependencies = [
        ('api', '0198_add_rainforest_alliance_certification'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
