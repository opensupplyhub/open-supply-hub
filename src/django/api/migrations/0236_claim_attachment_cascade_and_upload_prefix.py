from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    OSDEV-3370. Two changes to FacilityClaimAttachments:

    - claim FK moves from PROTECT to CASCADE. PROTECT made every
      facility deletion fail with ProtectedError whenever a claim
      carried attachments, because the facility delete path calls
      claim.delete() without clearing attachments first. The stored
      file is removed by the post_delete signal in api.signals.
    - claim_attachment gains upload_to='claim_attachments/' so new
      uploads land under a dedicated key prefix instead of the bucket
      root shared with facility list uploads. Existing objects are not
      moved; only new uploads are affected.
    """

    dependencies = [
        ('api', '0235_add_claimant_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityclaimattachments',
            name='claim',
            field=models.ForeignKey(
                help_text='The facility claim for this attachment file.',
                on_delete=django.db.models.deletion.CASCADE,
                to='api.facilityclaim',
            ),
        ),
        migrations.AlterField(
            model_name='facilityclaimattachments',
            name='claim_attachment',
            field=models.FileField(
                blank=True,
                help_text='The uploaded claimant attached file.',
                null=True,
                upload_to='claim_attachments/',
            ),
        ),
    ]
