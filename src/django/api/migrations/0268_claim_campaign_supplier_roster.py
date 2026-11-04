import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


FLAG_NAME = 'claim_campaign_self_serve'


def create_flag(apps, schema_editor):
    # Off for everyone except superusers. To enable a brand, add its
    # user(s) to the group of the same name in Django admin.
    Group = apps.get_model('auth', 'Group')
    group, _ = Group.objects.get_or_create(name=FLAG_NAME)

    Flag = apps.get_model('waffle', 'Flag')
    flag, _ = Flag.objects.get_or_create(
        name=FLAG_NAME,
        defaults={
            'everyone': None,
            'superusers': True,
            'staff': False,
            'note': (
                'Lets a brand create its own claims campaign from one of '
                'its lists (also needs the claim_campaigns switch). Add '
                'brand users to the group of the same name.'
            ),
        },
    )
    flag.groups.add(group)


def delete_flag(apps, schema_editor):
    Flag = apps.get_model('waffle', 'Flag')
    Flag.objects.filter(name=FLAG_NAME).delete()
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=FLAG_NAME).delete()


class Migration(migrations.Migration):
    """
    Gives claim campaigns an explicit supplier roster, validates the
    campaign code format, and adds the claim_campaign_self_serve flag.
    """

    dependencies = [
        ('api', '0267_create_claim_campaign'),
        ('waffle', '0004_update_everyone_nullbooleanfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimcampaign',
            name='code',
            field=models.CharField(
                help_text=(
                    'Unique human-readable campaign code used in claim '
                    'links.'
                ),
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message=(
                            'Use upper-case letters, digits and hyphens '
                            'only, starting with a letter or digit.'
                        ),
                        regex='^[A-Z0-9][A-Z0-9-]*$',
                    )
                ],
            ),
        ),
        migrations.CreateModel(
            name='ClaimCampaignSupplier',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(
                    help_text='The campaign that invites this production '
                              'location.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='suppliers',
                    to='api.claimcampaign')),
                ('facility', models.ForeignKey(
                    help_text='The invited production location.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='claim_campaign_suppliers',
                    to='api.facility')),
            ],
        ),
        migrations.AddConstraint(
            model_name='claimcampaignsupplier',
            constraint=models.UniqueConstraint(
                fields=('campaign', 'facility'),
                name='unique_claim_campaign_supplier',
            ),
        ),
        migrations.RunPython(create_flag, delete_flag),
    ]
