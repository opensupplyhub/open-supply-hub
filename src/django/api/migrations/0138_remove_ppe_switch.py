from django.db import migrations


def remove_ppe_switch(apps, schema_editor):
    '''
    This function removes the ppe switch.
    '''
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name='ppe').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0137_remove_ppe_fields'),
    ]

    operations = [
        migrations.RunPython(remove_ppe_switch)
    ]
