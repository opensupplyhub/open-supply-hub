# Generated by Django 3.2.4 on 2024-02-07 11:48

from api.models import ApiLimit
from django.db.migrations import RunPython
from django.db import migrations, models


def update_existing_apilimit_renewal_period(apps, schema_editor):
    api_limits = ApiLimit.objects.filter(renewal_period='')
    for api_limit in api_limits:
        api_limit.renewal_period = ApiLimit.YEARLY
        api_limit.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0136_remove_indexing_unnecessary_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='apilimit',
            name='renewal_period',
            field=models.CharField(blank=True, choices=[('MONTHLY', 'MONTHLY'), ('YEARLY', 'YEARLY')], help_text='Any limit set up on the 29th, 30th, or 31st will renew on the 1st of the following month.', max_length=200),
        ),
        migrations.AddField(
            model_name='historicalapilimit',
            name='renewal_period',
            field=models.CharField(blank=True, choices=[('MONTHLY', 'MONTHLY'), ('YEARLY', 'YEARLY')], help_text='Any limit set up on the 29th, 30th, or 31st will renew on the 1st of the following month.', max_length=200),
        ),
        migrations.RenameField(
            model_name='apilimit',
            old_name='yearly_limit',
            new_name='period_limit',
        ),
        migrations.RenameField(
            model_name='historicalapilimit',
            old_name='yearly_limit',
            new_name='period_limit',
        ),

        RunPython(update_existing_apilimit_renewal_period, RunPython.noop)
    ]
