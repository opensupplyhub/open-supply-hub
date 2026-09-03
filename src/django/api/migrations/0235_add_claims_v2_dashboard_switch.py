from django.db import migrations


SWITCH_NAME = 'enable_claims_v2_dashboard'


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
    Switch for the claims moderation dashboard v2 route
    (/dashboard/claims-v2). Created inactive so the route ships dark;
    see OSDEV-3355.
    """

    dependencies = [
        ('api', '0234_add_note_type_to_facility_claim_review_note'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]
