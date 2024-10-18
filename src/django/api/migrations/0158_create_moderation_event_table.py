# Generated by Django 3.2.17 on 2024-10-18 10:26

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0157_delete_endpoint_switcher_for_list_uploads'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date when the moderation queue entry was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Date when the moderation queue entry was last updated.')),
                ('status_change_date', models.DateTimeField(help_text='Date when the moderation decision was made.')),
                ('request_type', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('CLAIM', 'Claim')], help_text='Type of moderation record.', max_length=200)),
                ('raw_data', models.JSONField(default=dict, help_text='Key-value pairs of the non-parsed row and header for the moderation data.')),
                ('cleaned_data', models.JSONField(default=dict, help_text='Key-value pairs of the parsed row and header for the moderation data.')),
                ('geocode_result', models.JSONField(default=dict, help_text='Result of the geocode operation.')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RESOLVED', 'Resolved')], default='PENDING', help_text='Moderation status of the production location.', max_length=200)),
                ('source', models.CharField(choices=[('API', 'API'), ('SLC', 'SLC')], help_text='Source type of production location.', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='moderationevent',
            name='production_location_list_item',
            field=models.OneToOneField(help_text='Linked facility list item for this moderation queue entry.', on_delete=django.db.models.deletion.CASCADE, related_name='moderation_queue', to='api.facilitylistitem'),
        ),
    ]
