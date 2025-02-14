# Generated by Django 3.2.17 on 2024-11-26 16:27

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    '''
    This migration performs the following updates to the ModerationEvent table:
    1. Set uuid as the primary key.
    2. Make geocode_result field optional. It can be blank if lat and lng
    have been provided by user.
    3. Remove redundant blank=False and null=False constraints, as these are
    the default values for model fields in Django and do not need to be
    explicitly set.
    4. Make contributor field non-nullable, as the field should not be left
    empty. It is required to have information about the contributor.
    5. Allow claim field to be blank. This change reflects the fact that
    a moderation event may not always be related to a claim, so the field can
    be left empty.
    '''

    dependencies = [
        ('api', '0161_create_disable_list_uploading'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='moderationevent',
            name='id',
        ),
        migrations.AlterField(
            model_name='moderationevent',
            name='claim',
            field=models.OneToOneField(blank=True, help_text='Linked claim id for this production location.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderation_event_claim', to='api.facilityclaim'),
        ),
        migrations.AlterField(
            model_name='moderationevent',
            name='contributor',
            field=models.ForeignKey(help_text='Linked contributor responsible for this moderation event.', on_delete=django.db.models.deletion.PROTECT, related_name='moderation_event_contributor', to='api.contributor'),
        ),
        migrations.AlterField(
            model_name='moderationevent',
            name='geocode_result',
            field=models.JSONField(blank=True, default=dict, help_text='Result of the geocode operation.'),
        ),
        migrations.AlterField(
            model_name='moderationevent',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Unique identifier to make moderation event table more reusable across the app.', primary_key=True, serialize=False, unique=True),
        ),
    ]
