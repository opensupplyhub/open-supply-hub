from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration to record, per live claim check, when the claimant's page
    last asked for it and when its result was emailed to them.
    """

    dependencies = [
        ('api', '0272_facility_claim_live_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaimlivecheck',
            name='last_polled_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the claim form last asked for this '
                          'check. A result that arrives after the form '
                          'has stopped asking is emailed to the claimant '
                          'instead.',
                null=True),
        ),
        migrations.AddField(
            model_name='facilityclaimlivecheck',
            name='emailed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the result of this check was emailed to '
                          'the claimant. Empty when they saw it on the '
                          'page or there was nothing to send.',
                null=True),
        ),
    ]
