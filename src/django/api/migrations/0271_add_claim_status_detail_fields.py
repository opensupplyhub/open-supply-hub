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
    '''
    FacilityClaim = apps.get_model('api', 'FacilityClaim')
    FacilityClaimReviewNote = apps.get_model('api', 'FacilityClaimReviewNote')

    pending = FacilityClaim.objects.filter(status=PENDING)
    pending.update(waiting_on=OS_HUB)

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

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
    ]

    operations = [
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
        # Nothing to undo: reversing the migration drops the column the
        # backfill wrote to.
        migrations.RunPython(backfill_waiting_on, migrations.RunPython.noop),
        *[
            migrations.AlterField(
                model_name=model_name,
                name='waiting_on',
                field=waiting_on_field(default=OS_HUB),
            )
            for model_name in CLAIM_MODELS
        ],
    ]
