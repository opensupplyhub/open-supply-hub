from django.db import migrations
from django.db.models import F


def backfill_os_id_snapshot(apps, schema_editor):
    '''
    Forward-fill os_id_snapshot for approved ModerationEvent rows where the
    snapshot is still empty but os_id is present. Idempotent: rows that
    already have a snapshot are left untouched.

    Bulk update is safe here: os_id_snapshot has no signal handlers, so
    bypassing the ORM save() path has no side effects.
    '''
    ModerationEvent = apps.get_model('api', 'ModerationEvent')
    ModerationEvent.objects.filter(
        status='APPROVED',
        os_id_snapshot='',
        os_id__isnull=False,
    ).update(os_id_snapshot=F('os_id'))


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0213_add_os_id_snapshot_to_moderation_event'),
    ]

    operations = [
        migrations.RunPython(
            backfill_os_id_snapshot,
            migrations.RunPython.noop,
        ),
    ]
