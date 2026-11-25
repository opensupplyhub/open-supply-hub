from django.db import migrations, models
from django.db.models import F, OuterRef, Q, Subquery


PENDING = 'PENDING'
OS_HUB = 'OS_HUB'
CLAIMANT = 'CLAIMANT'
CLAIMANT_MESSAGE = 'CLAIMANT_MESSAGE'

WAITING_ON_CHOICES = [(OS_HUB, OS_HUB), (CLAIMANT, CLAIMANT)]
DENIAL_TYPE_CHOICES = [
    ('NO_RESPONSE', 'NO_RESPONSE'),
    ('NOT_ELIGIBLE', 'NOT_ELIGIBLE'),
]
AI_DECISION_CHOICES = [('APPROVED', 'APPROVED'), ('HELD', 'HELD')]

WAITING_ON_HELP_TEXT = (
    'Who has the next move while this claim is PENDING. OS_HUB = a '
    'moderator owes the next step (the claim is new, or the claimant '
    'updated it). CLAIMANT = the claimant was asked for something. '
    'Emptied on save once the claim is decided.'
)
DENIAL_TYPE_HELP_TEXT = (
    'Why this claim was DENIED. NO_RESPONSE = the claimant never '
    'answered. NOT_ELIGIBLE = a moderator reviewed the claim and ruled '
    'it out. Empty on claims that are not denied and on denials that '
    'have not been classified.'
)
AI_DECISION_HELP_TEXT = (
    'What the claims automation pipeline did with this claim. APPROVED '
    '= it approved the claim. HELD = it reviewed the claim and left it '
    'for a moderator. Empty when the pipeline has not reviewed the '
    'claim.'
)
AI_DECISION_REASON_HELP_TEXT = (
    'Why the claims automation pipeline made its decision.'
)

CLAIM_MODELS = ('facilityclaim', 'historicalfacilityclaim')
CLAIM_TABLES = ('api_facilityclaim', 'api_historicalfacilityclaim')

# The columns as Django's AddField would create them: nullable, no
# default, no index.
COLUMNS = (
    ('waiting_on', 'varchar(200)'),
    ('denial_type', 'varchar(200)'),
    ('ai_decision', 'varchar(200)'),
    ('ai_decision_reason', 'text'),
)


def add_columns_sql():
    return [
        'ALTER TABLE {} {};'.format(
            table,
            ', '.join(
                'ADD COLUMN IF NOT EXISTS {} {} NULL'.format(name, db_type)
                for name, db_type in COLUMNS
            ),
        )
        for table in CLAIM_TABLES
    ]


def drop_columns_sql():
    return [
        'ALTER TABLE {} {};'.format(
            table,
            ', '.join(
                'DROP COLUMN IF EXISTS {}'.format(name)
                for name, _ in COLUMNS
            ),
        )
        for table in reversed(CLAIM_TABLES)
    ]


def waiting_on_field(**kwargs):
    return models.CharField(
        blank=True,
        choices=WAITING_ON_CHOICES,
        help_text=WAITING_ON_HELP_TEXT,
        max_length=200,
        null=True,
        verbose_name='waiting on',
        **kwargs,
    )


def backfill_waiting_on(apps, schema_editor):
    '''
    Say who each open claim is waiting on. Decided claims and history
    rows keep the empty value the column was added with.

    A pending claim waits on the claimant when a message was emailed to
    them and they have not updated the claim since. Every other pending
    claim waits on OS Hub. Two UPDATE statements, no per-claim queries.

    Each row is written once: the claimant rows first, then OS Hub for
    the pending rows still empty. Every write to api_facilityclaim
    fires the claim indexing trigger, so setting every pending claim to
    OS Hub and then correcting some would index those twice.
    '''
    FacilityClaim = apps.get_model('api', 'FacilityClaim')
    FacilityClaimReviewNote = apps.get_model('api', 'FacilityClaimReviewNote')

    pending = FacilityClaim.objects.filter(status=PENDING)

    last_message_at = Subquery(
        FacilityClaimReviewNote.objects
        .filter(claim=OuterRef('pk'), note_type=CLAIMANT_MESSAGE)
        .order_by('-created_at')
        .values('created_at')[:1]
    )
    pending.annotate(
        last_message_at=last_message_at,
    ).filter(
        Q(claimant_updated_at__isnull=True)
        | Q(claimant_updated_at__lte=F('last_message_at')),
        last_message_at__isnull=False,
    ).update(waiting_on=CLAIMANT)

    pending.filter(waiting_on__isnull=True).update(waiting_on=OS_HUB)


class Migration(migrations.Migration):
    '''
    Adds the fields that refine a facility claim's status (OSDEV-3795):
    waiting_on, denial_type, ai_decision and ai_decision_reason, on
    FacilityClaim and its history table. The four status values do not
    change.

    waiting_on is added without a default so existing rows start empty,
    then backfilled for pending claims, then given its default for new
    claims. The default lives in Django, so that last step emits no SQL.
    '''

    # Adding a nullable column only updates the catalog, but it takes an
    # ACCESS EXCLUSIVE lock on api_facilityclaim, which every location
    # page reads. Non-atomic (like 0265) so that lock is released as soon
    # as the ALTER commits: in one transaction it would be held until the
    # backfill had finished, and the backfill fires the claim indexing
    # trigger for every pending claim. The lock_timeout makes an ALTER
    # fail fast instead of queueing behind a long-running query (and
    # every later read queueing behind it). The backfill then runs in
    # its own transaction and takes row locks only, so it blocks no
    # reads. Every step can be repeated (ADD COLUMN IF NOT EXISTS, and
    # the backfill rewrites the same values), so after a timeout the
    # recovery is rerunning migrate.
    atomic = False

    dependencies = [
        ('api', '0287_index_facet_arrays'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "SET lock_timeout = '5s';",
                        *add_columns_sql(),
                        'RESET lock_timeout;',
                    ],
                    reverse_sql=[
                        "SET lock_timeout = '5s';",
                        *drop_columns_sql(),
                        'RESET lock_timeout;',
                    ],
                ),
            ],
            state_operations=[
                *[
                    migrations.AddField(
                        model_name=model_name,
                        name='waiting_on',
                        field=waiting_on_field(),
                    )
                    for model_name in CLAIM_MODELS
                ],
                *[
                    migrations.AddField(
                        model_name=model_name,
                        name='denial_type',
                        field=models.CharField(
                            blank=True,
                            choices=DENIAL_TYPE_CHOICES,
                            help_text=DENIAL_TYPE_HELP_TEXT,
                            max_length=200,
                            null=True,
                            verbose_name='denial type',
                        ),
                    )
                    for model_name in CLAIM_MODELS
                ],
                *[
                    migrations.AddField(
                        model_name=model_name,
                        name='ai_decision',
                        field=models.CharField(
                            blank=True,
                            choices=AI_DECISION_CHOICES,
                            help_text=AI_DECISION_HELP_TEXT,
                            max_length=200,
                            null=True,
                            verbose_name='AI decision',
                        ),
                    )
                    for model_name in CLAIM_MODELS
                ],
                *[
                    migrations.AddField(
                        model_name=model_name,
                        name='ai_decision_reason',
                        field=models.TextField(
                            blank=True,
                            help_text=AI_DECISION_REASON_HELP_TEXT,
                            null=True,
                            verbose_name='AI decision reason',
                        ),
                    )
                    for model_name in CLAIM_MODELS
                ],
            ],
        ),
        # Nothing to undo: reversing the migration drops the column the
        # backfill wrote to.
        # One transaction for both UPDATEs, separate from the ALTERs
        # above, so the backfill is all or nothing.
        migrations.RunPython(
            backfill_waiting_on,
            migrations.RunPython.noop,
            atomic=True,
        ),
        *[
            migrations.AlterField(
                model_name=model_name,
                name='waiting_on',
                field=waiting_on_field(default=OS_HUB),
            )
            for model_name in CLAIM_MODELS
        ],
    ]
