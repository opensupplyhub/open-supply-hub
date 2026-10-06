import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Candidate validation votes and the pilot's moderator gate on
    retirement (OSDEV-3245, design decisions D4 and D6).

    Two new, initially empty tables:

    * api_facilitycandidatevote: one row per (facility, user), enforced by
      a unique constraint; the vote value is updated in place.
    * api_facilitycandidateretirementrequest: at most one open request per
      candidate (one-to-one on facility), opened when a vote write finds
      consensus-no while CANDIDATE_AUTO_RETIRE is off.

    Nothing on api_facility or api_user changes. Creating the tables is
    cheap, but each foreign key still takes a SHARE ROW EXCLUSIVE lock on
    the referenced table (api_facility, api_user) while the constraint is
    added, and that would queue behind a long-running transaction on
    either table, with every later writer queueing behind it. The
    lock_timeout makes the migration fail fast instead; it is atomic, so
    a timeout rolls everything back and rerunning migrate is the whole
    recovery.
    """

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0247_facility_alias_tombstone'),
    ]

    operations = [
        migrations.RunSQL(
            sql="SET lock_timeout = '5s';",
            reverse_sql="SET lock_timeout = '5s';",
        ),
        migrations.CreateModel(
            name='FacilityCandidateVote',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'vote',
                    models.CharField(
                        choices=[
                            ('confirmed', 'Confirmed'),
                            ('not_a_facility', 'Not a facility'),
                        ],
                        help_text=(
                            'Whether the voter believes the candidate is '
                            'a real facility (confirmed) or not '
                            '(not_a_facility).'
                        ),
                        max_length=14,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text='Moves when the voter changes their vote.',
                    ),
                ),
                (
                    'facility',
                    models.ForeignKey(
                        help_text=(
                            'The candidate facility this vote is about.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='candidate_votes',
                        to='api.facility',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        help_text='The account that cast the vote.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='candidate_votes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='facilitycandidatevote',
            constraint=models.UniqueConstraint(
                fields=('facility', 'user'),
                name='api_facilitycandidatevote_facility_user_uniq',
            ),
        ),
        migrations.CreateModel(
            name='FacilityCandidateRetirementRequest',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'tally',
                    models.JSONField(
                        help_text=(
                            'The vote tally when the request was opened or '
                            'last refreshed, e.g. {"confirmed": 1, '
                            '"not_a_facility": 5}.'
                        ),
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'Moves each time a new vote refreshes the tally.'
                        ),
                    ),
                ),
                (
                    'facility',
                    models.OneToOneField(
                        help_text=(
                            'The candidate whose tally reached consensus-no.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='candidate_retirement_request',
                        to='api.facility',
                    ),
                ),
            ],
            options={
                'verbose_name': 'candidate retirement request',
            },
        ),
        migrations.RunSQL(
            sql='RESET lock_timeout;',
            reverse_sql='RESET lock_timeout;',
        ),
    ]
