from django.db import migrations


SWITCH_NAME = 'slc_submission_quality_check'


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
    Migration to introduce a switch that controls the LLM-backed
    submission quality check on SLC location submissions. Created
    active so deploying this migration does not change behavior.
    """

    dependencies = [
        ('api', '0225_add_is_anonymized_to_source'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
