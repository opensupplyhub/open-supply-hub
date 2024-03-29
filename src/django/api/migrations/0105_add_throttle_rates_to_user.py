# Generated by Django 3.2.4 on 2022-09-08 17:26

import api.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0104_add_match_responsibility_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='burst_rate',
            field=models.CharField(default=api.models.get_default_burst_rate, help_text="Maximum allowed burst requests for this user. Burst rate should be shorter periods, 'second' or 'minute'. This applies to most API requests, but excludes Facility uploads.", max_length=20, validators=[django.core.validators.RegexValidator('\\d+/(second|minute|hour|day)', 'You must enter value of the format N/(second|minute|hour|day)')]),
        ),
        migrations.AddField(
            model_name='user',
            name='data_upload_rate',
            field=models.CharField(default=api.models.get_default_data_upload_rate, help_text='Maximum allowed facility upload rate for this user. This applies to only API Facility uploads.', max_length=20, validators=[django.core.validators.RegexValidator('\\d+/(second|minute|hour|day)', 'You must enter value of the format N/(second|minute|hour|day)')]),
        ),
        migrations.AddField(
            model_name='user',
            name='sustained_rate',
            field=models.CharField(default=api.models.get_default_sustained_rate, help_text="Maximum allowed sustained requests for this user. Sustained rate should be longer periods, 'hour' or 'day'. This applies to most API requests, but excludes Facility uploads.", max_length=20, validators=[django.core.validators.RegexValidator('\\d+/(second|minute|hour|day)', 'You must enter value of the format N/(second|minute|hour|day)')]),
        ),
    ]
