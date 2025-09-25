from django.db import migrations, models

class Migration(migrations.Migration):
    """
    Migration add unit field to PartnerField model.
    """

    dependencies = [
        ('api', '0180_add_unit_to_partner_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerfield',
            name='label',
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text=('The partner field label.')
            ),
        ),
    ]
