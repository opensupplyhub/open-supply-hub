from django.db import migrations

from api.constants import FeatureGroups


def create_can_get_union_linked_data(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(
        name=FeatureGroups.CAN_GET_UNION_LINKED_DATA
    )


def remove_can_get_union_linked_data(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name=FeatureGroups.CAN_GET_UNION_LINKED_DATA
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0216_backfill_moderation_event_os_id_snapshot'),
    ]

    operations = [
        migrations.RunPython(
            create_can_get_union_linked_data,
            remove_can_get_union_linked_data,
        ),
    ]
