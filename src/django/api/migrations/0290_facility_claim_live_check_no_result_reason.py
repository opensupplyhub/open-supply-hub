from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds no_result_reason to FacilityClaimLiveCheck (OSDEV-3911): why
    the claims automation pipeline ended a live check without a result.
    A text column with a constant default on a table that 0289 has only
    just created, so no row is rewritten.
    """

    dependencies = [
        ('api', '0289_facility_claim_live_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaimlivecheck',
            name='no_result_reason',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Why the pipeline ended this check without a '
                          'result, as it reported it (for example '
                          'review_in_progress or failed). Empty when it '
                          'gave a result or reported nothing.',
                max_length=200,
            ),
        ),
    ]
