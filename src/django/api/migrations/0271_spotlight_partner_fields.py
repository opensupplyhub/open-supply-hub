import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models

import api.models.spotlight_field

NAME_RULES = (
    'Use only lowercase letters, numbers and underscores, start with a '
    'letter, and keep it to 50 characters or fewer (for example '
    '"certification_status").'
)
DISPLAY_NAME_RULES = 'Keep the display name to 50 characters or fewer.'
NAME_HELP = f'Internal name. Cannot change once saved. {NAME_RULES}'
DISPLAY_NAME_HELP = f'Name shown on OS Hub. {DISPLAY_NAME_RULES}'
FIELD_TYPE_HELP = (
    'The kind of value this field holds. Cannot change once saved.'
)
FIELD_TYPE_CHOICES = [
    ('text', 'Text'),
    ('date', 'Date'),
    ('number', 'Number'),
    ('yes_no', 'Yes/No'),
    ('score', 'Score / Rating'),
    ('url', 'URL'),
]
APPROVED_HELP = (
    'New fields need admin approval before they can be active.'
)
ACTIVE_HELP = 'Inactive fields appear nowhere on the site.'
GO_LIVE_HELP = (
    'Until this date the partner cannot activate fields. On this '
    'date every approved field is switched on automatically. '
    'Leave blank for no date. Changing it may deactivate fields '
    'that are currently active.'
)


class Migration(migrations.Migration):
    """
    Spotlight partner self-serve fields (OSDEV-3788).

    Adds the two permission flags on `Contributor`, the per-partner
    `SpotlightField` (wrapping the partner's single object-type
    `PartnerField`, with the go-live date) and `SpotlightFieldProperty`
    (each field inside it, plus its history table).
    """

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='is_spotlight_partner',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Gives this contributor a Spotlight section in their '
                    'dashboard where they can create and manage their own '
                    'Spotlight fields. Fields they add need admin approval '
                    'before they can be active.'
                ),
                verbose_name='Spotlight partner',
            ),
        ),
        migrations.AddField(
            model_name='contributor',
            name='can_control_spotlight_visibility',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Lets a Spotlight partner choose whether their fields '
                    'appear in the API and in data downloads. Fields are '
                    'visible in both by default.'
                ),
                verbose_name=(
                    'Can control Spotlight visibility in API and downloads'
                ),
            ),
        ),
        migrations.AddField(
            model_name='historicalcontributor',
            name='is_spotlight_partner',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Gives this contributor a Spotlight section in their '
                    'dashboard where they can create and manage their own '
                    'Spotlight fields. Fields they add need admin approval '
                    'before they can be active.'
                ),
                verbose_name='Spotlight partner',
            ),
        ),
        migrations.AddField(
            model_name='historicalcontributor',
            name='can_control_spotlight_visibility',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Lets a Spotlight partner choose whether their fields '
                    'appear in the API and in data downloads. Fields are '
                    'visible in both by default.'
                ),
                verbose_name=(
                    'Can control Spotlight visibility in API and downloads'
                ),
            ),
        ),
        migrations.CreateModel(
            name='SpotlightField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('go_live_date', models.DateField(
                    blank=True, help_text=GO_LIVE_HELP, null=True)),
                ('go_live_applied', models.BooleanField(
                    default=False,
                    help_text=(
                        'Set once the go-live date has switched the fields '
                        'on.'
                    ))),
                ('last_partner_edit_at', models.DateTimeField(
                    blank=True, db_index=True,
                    help_text='When the partner last edited one of these '
                              'fields.',
                    null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contributor', models.OneToOneField(
                    help_text='The Spotlight partner who owns these fields.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='spotlight_field',
                    to='api.contributor')),
                ('partner_field', models.OneToOneField(
                    help_text=('The object-type partner field the '
                               'properties live in.'),
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='spotlight_field',
                    to='api.partnerfield')),
            ],
            options={
                'verbose_name': 'Spotlight field set',
                'verbose_name_plural': 'Spotlight field sets',
            },
        ),
        migrations.CreateModel(
            name='SpotlightFieldProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text=NAME_HELP, max_length=50,
                    validators=[
                        api.models.spotlight_field.validate_internal_name
                    ])),
                ('display_name', models.CharField(
                    help_text=DISPLAY_NAME_HELP, max_length=50)),
                ('field_type', models.CharField(
                    choices=FIELD_TYPE_CHOICES, default='text',
                    help_text=FIELD_TYPE_HELP, max_length=20)),
                ('approved', models.BooleanField(
                    default=False, help_text=APPROVED_HELP)),
                ('approved_at', models.DateTimeField(
                    blank=True, null=True)),
                ('active', models.BooleanField(
                    default=False, help_text=ACTIVE_HELP)),
                ('last_partner_edit_at', models.DateTimeField(
                    blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL)),
                ('spotlight_field', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='properties',
                    to='api.spotlightfield')),
            ],
            options={
                'verbose_name': 'Spotlight field',
                'verbose_name_plural': 'Spotlight fields',
                'ordering': ('id',),
                'unique_together': {('spotlight_field', 'name')},
            },
        ),
        migrations.CreateModel(
            name='HistoricalSpotlightFieldProperty',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True,
                                           db_index=True, verbose_name='ID')),
                ('name', models.CharField(
                    help_text=NAME_HELP, max_length=50,
                    validators=[
                        api.models.spotlight_field.validate_internal_name
                    ])),
                ('display_name', models.CharField(
                    help_text=DISPLAY_NAME_HELP, max_length=50)),
                ('field_type', models.CharField(
                    choices=FIELD_TYPE_CHOICES, default='text',
                    help_text=FIELD_TYPE_HELP, max_length=20)),
                ('approved', models.BooleanField(
                    default=False, help_text=APPROVED_HELP)),
                ('approved_at', models.DateTimeField(
                    blank=True, null=True)),
                ('active', models.BooleanField(
                    default=False, help_text=ACTIVE_HELP)),
                ('last_partner_edit_at', models.DateTimeField(
                    blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True,
                                                    editable=False)),
                ('updated_at', models.DateTimeField(blank=True,
                                                    editable=False)),
                ('history_id', models.AutoField(primary_key=True,
                                                serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100,
                                                           null=True)),
                ('history_type', models.CharField(
                    choices=[('+', 'Created'), ('~', 'Changed'),
                             ('-', 'Deleted')],
                    max_length=1)),
                ('approved_by', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL)),
                ('spotlight_field', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='api.spotlightfield')),
            ],
            options={
                'verbose_name': 'historical Spotlight field',
                'verbose_name_plural': 'historical Spotlight fields',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
