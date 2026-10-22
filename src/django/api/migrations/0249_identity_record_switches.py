from django.db import migrations

SWITCHES = (
    'enable_identity_resolver',
    'enable_identity_record_registration',
)


class Migration(migrations.Migration):
    """
    Creates the two pilot switches, inactive, where they are not already
    present. Created here rather than left absent so the levers are
    visible in the Django admin of every environment.
    """

    def create_identity_record_switches(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        for name in SWITCHES:
            Switch.objects.get_or_create(
                name=name, defaults={'active': False}
            )

    def delete_identity_record_switches(apps, schema_editor):
        Switch = apps.get_model('waffle', 'Switch')
        Switch.objects.filter(name__in=SWITCHES).delete()

    dependencies = [
        ('api', '0248_identity_record_association'),
        ('waffle', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_identity_record_switches,
            delete_identity_record_switches,
        )
    ]
