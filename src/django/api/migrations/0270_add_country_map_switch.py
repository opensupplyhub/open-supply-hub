from django.db import migrations


def create_country_map_switch(apps, schema_editor):
    '''
    Gates the country-level map that replaces the vector tile map on the
    search page. Off on creation: the map renders but nothing in the sidebar
    reacts to it yet.
    '''
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name='country_map',
        defaults={'active': False},
    )


def delete_country_map_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name='country_map').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0269_country_stats'),
    ]

    operations = [
        migrations.RunPython(
            create_country_map_switch,
            delete_country_map_switch,
        )
    ]
