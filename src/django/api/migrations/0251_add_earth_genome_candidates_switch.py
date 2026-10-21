from django.db import migrations


SWITCH_NAME = 'earth_genome_candidates'


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
    Migration to introduce the switch that turns the Earth Genome
    candidate pilot on or off per environment (OSDEV-3627): the ingest
    command, the vote and retirement-request endpoints and the
    candidate detail / bbox responses. Created inactive everywhere;
    staff enable it in the Django admin (Waffle > Switches) when an
    environment is ready for the pilot. The candidate exclusions and the
    contributor guard are not behind it.
    """

    dependencies = [
        ('api', '0250_facility_candidate_vote'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
