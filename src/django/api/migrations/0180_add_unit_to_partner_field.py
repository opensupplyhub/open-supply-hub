from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    """
    Migration add unit to PartnerField model and update partner_fields of Contributor model.
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

        migrations.AlterField(
            model_name='contributor',
            name='partner_fields',
            field=models.ManyToManyField(
                blank=True,
                help_text='Partner fields that this contributor can access',
                to='api.partnerfield'
            ),
        ),
    ]
