import uuid

import django.db.models.deletion
from django.db import migrations, models


SWITCH_NAME = 'claim_campaigns'


def create_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Migration to introduce the ClaimCampaign model, the campaign and
    via_link fields on FacilityClaim, and the claim_campaigns switch.
    """

    dependencies = [
        ('api', '0217_add_contribution_dates_to_index_contributors'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimCampaign',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('uuid', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    help_text='Unique identifier for the claim campaign.',
                    unique=True)),
                ('name', models.CharField(
                    help_text='The campaign name.',
                    max_length=200)),
                ('code', models.CharField(
                    help_text=(
                        'Unique human-readable campaign code used in '
                        'claim links.'
                    ),
                    max_length=50,
                    unique=True)),
                ('status', models.CharField(
                    choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')],
                    default='ACTIVE',
                    help_text='The campaign status.',
                    max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contributor', models.ForeignKey(
                    help_text='The contributor who owns this claim campaign.',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='api.contributor')),
            ],
        ),
        migrations.AddField(
            model_name='facilityclaim',
            name='campaign',
            field=models.ForeignKey(
                blank=True,
                help_text='The claim campaign this claim is attributed to.',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='api.claimcampaign'),
        ),
        migrations.AddField(
            model_name='facilityclaim',
            name='via_link',
            field=models.BooleanField(
                default=False,
                help_text='Whether the claim was submitted via a campaign '
                          'link.'),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='campaign',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text='The claim campaign this claim is attributed to.',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='+',
                to='api.claimcampaign'),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='via_link',
            field=models.BooleanField(
                default=False,
                help_text='Whether the claim was submitted via a campaign '
                          'link.'),
        ),
        migrations.RunPython(create_switch, delete_switch),
    ]
