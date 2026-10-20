import django.contrib.postgres.fields
import django.db.models.deletion
import django.db.models.functions.text
import simple_history.models
from django.conf import settings
from django.db import migrations, models

NAME_HELP = (
    'The name shown in the claim form and stored on claims. Renaming it '
    'also updates every existing claim that holds the old name. 50 '
    'characters at most.'
)
IS_ACTIVE_HELP = (
    'Whether the claim form offers this option. Untick it to stop offering '
    'an option without touching the claims that already hold it.'
)
SORT_ORDER_HELP = (
    'Position in the dropdown; lower numbers come first. Options with the '
    'same number are sorted by name.'
)
UNIQUE_CI_MESSAGE = (
    'An option with this name already exists (names are compared ignoring '
    'case).'
)
AFFILIATION_HELP = (
    'A group the facility is affiliated with. Offered values are managed '
    'as ClaimAffiliation options.'
)
CERTIFICATION_HELP = (
    'A certification the facility has achieved. Offered values are '
    'managed as ClaimCertification options.'
)


class Migration(migrations.Migration):
    """
    Move the claim form's Affiliations and Certifications/Standards/
    Regulations lists out of hard-coded `choices` and into two tables
    (plus their history tables) managed in the Django admin. See
    OSDEV-2219.

    The `AlterField` operations only drop `choices` and reword
    `help_text` on the claim array fields: the columns themselves
    (varchar(50)[]) are unchanged, so they emit no SQL. This is the last
    migration a list change will need; from here on options are rows.
    The tables are seeded in 0249.
    """

    dependencies = [
        ('api', '0247_add_zone_set_and_zone'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimAffiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text=NAME_HELP, max_length=50, unique=True)),
                ('is_active', models.BooleanField(
                    default=True, help_text=IS_ACTIVE_HELP)),
                ('sort_order', models.PositiveIntegerField(
                    default=0, help_text=SORT_ORDER_HELP)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'claim affiliation',
                'verbose_name_plural': 'claim affiliations',
                'ordering': ('sort_order', 'name'),
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='claimaffiliation',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                name='api_claimaffiliation_name_ci_unique',
                violation_error_message=UNIQUE_CI_MESSAGE,
            ),
        ),
        migrations.CreateModel(
            name='HistoricalClaimAffiliation',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True,
                                           db_index=True, verbose_name='ID')),
                ('name', models.CharField(
                    db_index=True, help_text=NAME_HELP, max_length=50)),
                ('is_active', models.BooleanField(
                    default=True, help_text=IS_ACTIVE_HELP)),
                ('sort_order', models.PositiveIntegerField(
                    default=0, help_text=SORT_ORDER_HELP)),
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
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical claim affiliation',
                'verbose_name_plural': 'historical claim affiliations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ClaimCertification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text=NAME_HELP, max_length=50, unique=True)),
                ('is_active', models.BooleanField(
                    default=True, help_text=IS_ACTIVE_HELP)),
                ('sort_order', models.PositiveIntegerField(
                    default=0, help_text=SORT_ORDER_HELP)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'claim certification/standard/regulation',
                'verbose_name_plural': 'claim certifications/standards/regulations',
                'ordering': ('sort_order', 'name'),
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='claimcertification',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                name='api_claimcertification_name_ci_unique',
                violation_error_message=UNIQUE_CI_MESSAGE,
            ),
        ),
        migrations.CreateModel(
            name='HistoricalClaimCertification',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True,
                                           db_index=True, verbose_name='ID')),
                ('name', models.CharField(
                    db_index=True, help_text=NAME_HELP, max_length=50)),
                ('is_active', models.BooleanField(
                    default=True, help_text=IS_ACTIVE_HELP)),
                ('sort_order', models.PositiveIntegerField(
                    default=0, help_text=SORT_ORDER_HELP)),
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
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical claim certification/standard/regulation',
                'verbose_name_plural': 'historical claim certifications/standards/regulations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_affiliations',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    help_text=AFFILIATION_HELP,
                    max_length=50,
                    verbose_name='facility affiliation',
                ),
                blank=True,
                help_text="The facility's affiliations",
                null=True,
                size=None,
                verbose_name='facility affilations',
            ),
        ),
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_certifications',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    help_text=CERTIFICATION_HELP,
                    max_length=50,
                    verbose_name='facility certification',
                ),
                blank=True,
                help_text="The facility's certifications",
                null=True,
                size=None,
                verbose_name='facility certifications',
            ),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_affiliations',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    help_text=AFFILIATION_HELP,
                    max_length=50,
                    verbose_name='facility affiliation',
                ),
                blank=True,
                help_text="The facility's affiliations",
                null=True,
                size=None,
                verbose_name='facility affilations',
            ),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_certifications',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    help_text=CERTIFICATION_HELP,
                    max_length=50,
                    verbose_name='facility certification',
                ),
                blank=True,
                help_text="The facility's certifications",
                null=True,
                size=None,
                verbose_name='facility certifications',
            ),
        ),
    ]
