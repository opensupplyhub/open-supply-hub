import django.db.models.deletion
from django.db import migrations, models


FLAG_NAME = 'claim_campaign_email_invites'


def create_flag(apps, schema_editor):
    # Off for everyone except superusers. To let a brand have OS Hub email
    # claim invites from its campaigns, add its user(s) to the group of
    # the same name (or use the Django admin action on Claim campaigns).
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
                'Brands allowed to have OS Hub email claim invites to their '
                'suppliers from a claims campaign (on top of '
                'claim_campaign_access and the claim_invite switch). Add '
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

    dependencies = [
        ('api', '0268_claim_campaign_supplier_roster'),
        ('waffle', '0004_update_everyone_nullbooleanfield'),
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
        migrations.RunPython(create_flag, delete_flag),
    ]
