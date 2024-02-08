# Generated by Django 3.2.4 on 2024-02-07 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0135_disable_duplicates_and_lowercase_all_emails'),
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
    ]
