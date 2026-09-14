from django.db import migrations


SWITCH_NAME = 'enable_claim_name_address_edit'


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
    Switch that lets a claimant edit the Company Name and Company Address
    fields in the claim form's Business step, and shows the matching
    document/SLC guidance. Created inactive so the change ships dark;
    see OSDEV-3404.
    """

    dependencies = [
        ('api', '0238_add_claims_v2_dashboard_switch'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
