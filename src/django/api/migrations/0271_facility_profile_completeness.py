import django.db.models.deletion
from django.db import migrations, models


FLAG_NAME = 'show_profile_completeness'


def create_flag(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Flag = apps.get_model('waffle', 'Flag')
    group, _ = Group.objects.get_or_create(name=FLAG_NAME)
    flag, _ = Flag.objects.get_or_create(
        name=FLAG_NAME,
        defaults={
            'everyone': None,
            'superusers': True,
            'staff': False,
            'note': (
                'Admin-only preview of the profile completeness indicator '
                'on production location profiles. On for superusers; add '
                'other users to the group of the same name.'
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
    Creates the table holding each run's profile completeness score and
    model-backed classification per production location, and the
    show_profile_completeness flag (with an auth group of the same name)
    that limits the preview to superusers and group members.
    """

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
        ('waffle', '0004_update_everyone_nullbooleanfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityProfileCompleteness',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('run_date', models.DateField(
                    help_text=(
                        'The date the score and/or classification was '
                        'computed.'
                    ),
                )),
                ('score', models.FloatField(
                    blank=True,
                    help_text='Profile completeness score from 0 to 1.',
                    null=True,
                )),
                ('components', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text=(
                        'The scorer components the score averages, each 0 '
                        'to 1.'
                    ),
                )),
                ('scorer_version', models.CharField(
                    blank=True,
                    max_length=50,
                )),
                ('classifier_tier', models.CharField(
                    blank=True,
                    choices=[
                        ('low', 'low'),
                        ('medium', 'medium'),
                        ('high', 'high'),
                    ],
                    help_text=(
                        'Final tier from the model-backed classification.'
                    ),
                    max_length=10,
                )),
                ('classifier_agreement_tier', models.CharField(
                    blank=True,
                    choices=[
                        ('low', 'low'),
                        ('medium', 'medium'),
                        ('high', 'high'),
                        ('best', 'best'),
                    ],
                    help_text=(
                        'Contributor agreement check of the classification.'
                    ),
                    max_length=10,
                )),
                ('classifier_field_tier', models.CharField(
                    blank=True,
                    choices=[
                        ('low', 'low'),
                        ('medium', 'medium'),
                        ('high', 'high'),
                    ],
                    help_text='Field data check of the classification.',
                    max_length=10,
                )),
                ('classifier_model', models.CharField(
                    blank=True,
                    help_text=(
                        'Name and version of the model that classified it.'
                    ),
                    max_length=100,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('facility', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile_completeness_runs',
                    to='api.facility',
                )),
            ],
            options={
                'verbose_name': 'profile completeness run',
                'verbose_name_plural': 'profile completeness runs',
                'ordering': ('-run_date',),
                'unique_together': {('facility', 'run_date')},
            },
        ),
        migrations.RunPython(create_flag, delete_flag),
    ]
