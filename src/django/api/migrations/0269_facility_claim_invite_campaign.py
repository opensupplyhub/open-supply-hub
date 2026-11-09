import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0268_claim_campaign_supplier_roster'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaiminvite',
            name='campaign',
            field=models.ForeignKey(
                blank=True,
                help_text='The claims campaign the invite was sent from, if '
                          'any. Its code is added to the claim link.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invites',
                to='api.claimcampaign',
            ),
        ),
    ]
