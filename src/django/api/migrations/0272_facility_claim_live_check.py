import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


SWITCH_NAME = 'claim_live_check'

STATUS_CHOICES = [
    ('CHECKING', 'CHECKING'),
    ('PASSED', 'PASSED'),
    ('NOT_PASSED', 'NOT_PASSED'),
    ('UNAVAILABLE', 'UNAVAILABLE'),
]


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
    Migration to introduce the FacilityClaimLiveCheck model and the
    claim_live_check switch (off).
    """

    dependencies = [
        ('api', '0271_add_claim_status_detail_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityClaimLiveCheck',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('status', models.CharField(
                    choices=STATUS_CHOICES,
                    default='CHECKING',
                    help_text='Where the check stands. CHECKING = the '
                              'claims automation pipeline was asked and '
                              'has not answered. PASSED = the claim was '
                              'approved. NOT_PASSED = the pipeline held '
                              'the claim. UNAVAILABLE = the check could '
                              'not run or did not answer in time.',
                    max_length=200)),
                ('fixes', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=200),
                    blank=True,
                    default=list,
                    help_text='Keys of the preset fixes shown to the '
                              'claimant when the check did not pass. '
                              'Empty otherwise.',
                    size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('claim', models.ForeignKey(
                    help_text='The facility claim that was checked.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='live_checks',
                    to='api.facilityclaim')),
            ],
        ),
        migrations.RunPython(create_switch, delete_switch),
    ]
