from django.db import migrations, models


class Migration(migrations.Migration):
    """
    OSDEV-3371. Adds FacilityClaim.claimant_updated_at, stamped only by
    the claimant-facing pending-claim edit endpoints (field edits and
    attachment changes), so the claims queue can show and sort by the
    last claimant update without conflating moderator edits, which also
    bump updated_at.
    """

    dependencies = [
        ('api', '0234_claim_attachment_cascade_and_upload_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaim',
            name='claimant_updated_at',
            field=models.DateTimeField(
                blank=True,
                help_text=(
                    'When the claimant last updated this claim or its '
                    'attachments through the pending-claim edit flow.'
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='claimant_updated_at',
            field=models.DateTimeField(
                blank=True,
                help_text=(
                    'When the claimant last updated this claim or its '
                    'attachments through the pending-claim edit flow.'
                ),
                null=True,
            ),
        ),
    ]
