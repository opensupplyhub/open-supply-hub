import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


ACCESS_FLAG = 'claim_campaign_access'
SELF_SERVE_FLAG = 'claim_campaign_self_serve'

# Both are off for everyone except superusers. To turn a brand on, add
# its user(s) to the group of the same name in Django admin (or use the
# "Give these brands campaign access" action on Claim campaigns).
FLAGS = {
    ACCESS_FLAG: (
        'Claims campaigns are a premium feature: brand users in the group '
        'of the same name see Claims Campaigns in their account menu, '
        'their campaigns, and can invite suppliers and close campaigns. '
        'Also needs the claim_campaigns switch.'
    ),
    SELF_SERVE_FLAG: (
        'Lets a brand create its own claims campaigns (on top of '
        'claim_campaign_access). Add brand users to the group of the same '
        'name.'
    ),
}


def create_flags(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Flag = apps.get_model('waffle', 'Flag')
    for name, note in FLAGS.items():
        group, _ = Group.objects.get_or_create(name=name)
        flag, _ = Flag.objects.get_or_create(
            name=name,
            defaults={
                'everyone': None,
                'superusers': True,
                'staff': False,
                'note': note,
            },
        )
        flag.groups.add(group)


def delete_flags(apps, schema_editor):
    Flag = apps.get_model('waffle', 'Flag')
    Flag.objects.filter(name__in=FLAGS).delete()
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=FLAGS).delete()


class Migration(migrations.Migration):
    """
    Gives claim campaigns an explicit supplier roster, validates the
    campaign code format, and adds the claim_campaign_access (premium) and
    claim_campaign_self_serve flags.
    """

    dependencies = [
        ('api', '0269_create_claim_campaign'),
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
        migrations.AddField(
            model_name='claimcampaign',
            name='uses_roster',
            field=models.BooleanField(
                default=False,
                verbose_name='chosen suppliers only',
                help_text=(
                    'On: the campaign invites only the suppliers listed '
                    'below, even if that list becomes empty. Off (v1): it '
                    'covers every production location on the brand\'s '
                    'active lists. Turned on automatically when suppliers '
                    'are chosen.'
                ),
            ),
        ),
        migrations.RunPython(create_flags, delete_flags),
    ]
