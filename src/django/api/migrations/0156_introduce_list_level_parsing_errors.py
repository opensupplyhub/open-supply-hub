# Generated by Django 3.2.4 on 2024-09-27 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0155_remove_verification_method_column_from_facility_claim'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilitylist',
            name='parsing_errors',
            field=models.JSONField(
                default=list,
                help_text=('List-level and internal errors logged '
                           'during background parsing of the list.')),
        )
    ]