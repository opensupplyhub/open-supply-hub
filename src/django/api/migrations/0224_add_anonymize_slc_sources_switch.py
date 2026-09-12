from django.db import migrations


SWITCH_NAME = 'anonymize_slc_sources'


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
    Migration to introduce a switch that anonymizes sources created for
    approved SLC moderation events by marking them non-public.
    """

    dependencies = [
        ('api', '0223_fix_sector_search_index'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
