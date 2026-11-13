from django.db import migrations


SWITCH_NAMES = (
    'embed_facility_dots',
    'embed_production_location_page',
)


def create_switches(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    for name in SWITCH_NAMES:
        Switch.objects.get_or_create(name=name, defaults={'active': False})


def delete_switches(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name__in=SWITCH_NAMES).delete()


class Migration(migrations.Migration):
    """
    Adds the switches two changes to every embedded map sit behind: drawing
    facilities as dots at every zoom level, and opening a location on the
    production location page layout. Both are created off, so no embedded
    map changes until they are turned on.
    """

    dependencies = [
        ('api', '0280_embedfield_explanations'),
    ]

    operations = [
        migrations.RunPython(create_switches, delete_switches),
    ]
