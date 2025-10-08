from django.db import migrations, models

class Migration(migrations.Migration):
    """
    Migration add unit field to PartnerField model.
    """

    dependencies = [
        ('api', '0179_introduce_enable_v1_claims_flow'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerfield',
            name='unit',
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text=('The partner field unit.')
            ),
        ),
    ]
