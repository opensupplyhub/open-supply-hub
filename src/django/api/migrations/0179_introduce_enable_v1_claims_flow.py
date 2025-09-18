from django.db import migrations


def create_enable_v1_claims_flow_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name='enable_v1_claims_flow',
        defaults={'active': False},
    )


def delete_enable_v1_claims_flow_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name='enable_v1_claims_flow').delete()


class Migration(migrations.Migration):
    """
    Migration to introduce a switch for enabling v1 claims flow.
    """

    dependencies = [
        ('api', '0178_add_partner_fields_to_contributor'),
    ]

    operations = [
        migrations.RunPython(
            create_enable_v1_claims_flow_switch,
            delete_enable_v1_claims_flow_switch,
        )
    ]
