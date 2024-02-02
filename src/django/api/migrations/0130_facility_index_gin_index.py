
from django.db.migrations import Migration
from django.db import migrations
from django.contrib.postgres.operations import BtreeGinExtension
import django.contrib.postgres.indexes

class Migration(Migration):

    dependencies = [
        ('api', '0129_delete_facility_index'),
    ]

    operations = [
        BtreeGinExtension(),
        migrations.AddIndex(
            model_name='facilityindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['contrib_types', 'contributors_id', 'lists'], name='api_facilit_contrib_aa2da9_gin'),
        ),
    ]
