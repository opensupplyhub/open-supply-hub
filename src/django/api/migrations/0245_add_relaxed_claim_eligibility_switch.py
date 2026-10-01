from django.db import migrations

SWITCH_NAME = 'relaxed_claim_eligibility'


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

    dependencies = [
        # Follows #1307's 0244 (OSDEV-3489), which also branched from
        # 0243, so the api migration graph keeps a single leaf.
        ('api', '0244_add_claim_quality_check_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
