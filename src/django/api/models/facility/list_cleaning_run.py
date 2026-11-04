"""
Results of the Cornell list-cleaning pipeline (OSDEV-3726) for one upload.

A ``ListCleaningRun`` is one invocation of the pipeline for a facility list.
Each thing the pipeline said about a row is a ``ListCleaningSuggestion``: a
suggested correction, an issue to flag, or a row removal. The contributor's
(or moderator's) decision is recorded on the suggestion itself, so every
accept / reject / edit is logged per row and per code, which is what the
per-code agreement rates in OSDEV-3399 need.
"""
from django.db import models


class ListCleaningRun(models.Model):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (RUNNING, RUNNING),
        (COMPLETE, COMPLETE),
        (FAILED, FAILED),
    )

    STEP_FUNCTIONS = 'stepfunctions'
    STUB = 'stub'
    IMPORT = 'import'
    RUNNER_CHOICES = (
        (STEP_FUNCTIONS, 'AWS Step Functions'),
        (STUB, 'Local stub rules'),
        (IMPORT, 'Imported records file'),
    )

    facility_list = models.ForeignKey(
        'FacilityList',
        on_delete=models.CASCADE,
        related_name='cleaning_runs',
        help_text='The list this run was started for.')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING)
    runner = models.CharField(
        max_length=20,
        choices=RUNNER_CHOICES,
        default=STEP_FUNCTIONS,
        help_text='What executed the pipeline for this run.')
    execution_arn = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Step Functions execution ARN, when the runner is '
                  'stepfunctions.')
    prompt_version = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='PromptVersion the pipeline reported for this run.')
    file_pass = models.JSONField(
        default=dict,
        blank=True,
        help_text='List-level findings from stage 1: header issues, '
                  'repeated names, exact duplicates.')
    usage = models.JSONField(
        default=dict,
        blank=True,
        help_text='Token usage and wall-clock reported by the pipeline.')
    error = models.TextField(
        blank=True,
        default='',
        help_text='Why the run failed, if it did.')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When accepted corrections were last applied to the list.')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'ListCleaningRun {self.id} for list {self.facility_list_id}'


class ListCleaningSuggestion(models.Model):
    CORRECTION = 'CORRECTION'
    ISSUE = 'ISSUE'
    REMOVAL = 'REMOVAL'
    KIND_CHOICES = (
        (CORRECTION, 'Suggested correction'),
        (ISSUE, 'Issue'),
        (REMOVAL, 'Row removal'),
    )

    MUST_FIX = 'must_fix'
    INTERNAL_NOTE = 'internal_note'
    SEVERITY_CHOICES = (
        (MUST_FIX, MUST_FIX),
        (INTERNAL_NOTE, INTERNAL_NOTE),
    )

    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    EDITED = 'EDITED'
    REMOVED = 'REMOVED'  # contributor chose to drop the row instead
    DECISION_CHOICES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (EDITED, EDITED),
        (REMOVED, REMOVED),
    )

    # Fields the pipeline may flag but must never change (handoff §2,
    # OSDEV-3725). A correction the model emits for one of these is kept
    # visible but is never pre-accepted.
    PROTECTED_FIELDS = ('name', 'address')

    # Corrections the prompt applies silently (§4 "internal"). The prototype
    # shows them but pre-accepts them so a contributor who does nothing still
    # gets the formatting fixes; rejecting one is a recorded decision.
    SILENT_CORRECTION_CODES = (
        'whitespace', 'quotes', 'filler_text', 'encoding', 'country_code',
        'separators', 'workers_format', 'casing',
    )

    run = models.ForeignKey(
        ListCleaningRun,
        on_delete=models.CASCADE,
        related_name='suggestions')
    facility_list_item = models.ForeignKey(
        'FacilityListItem',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='cleaning_suggestions',
        help_text='The row this suggestion is about. Null for findings '
                  'the pipeline reported for a row that has no item.')
    row_number = models.IntegerField(
        help_text='Row number as in the spreadsheet (first data row is 2).')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    field = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Column the suggestion applies to, when it is one column.')
    code = models.CharField(
        max_length=100,
        help_text='Reason code (corrections) or issue code (issues) from '
                  'the prompt catalog. Several codes joined by "+" when '
                  'the model applied more than one rule to a field.')
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        blank=True,
        default='',
        help_text='Issues only. internal_note is never shown to the '
                  'contributor.')
    original_value = models.TextField(blank=True, default='')
    corrected_value = models.TextField(blank=True, default='')
    note = models.TextField(
        blank=True,
        default='',
        help_text='The one-sentence plain-language explanation.')
    extra = models.JSONField(
        default=dict,
        blank=True,
        help_text='Anything else the record carried, e.g. duplicate_of.')

    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default=PENDING)
    decided_value = models.TextField(
        blank=True,
        default='',
        help_text='The value the contributor typed, when decision is '
                  'EDITED.')
    decided_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Null when the decision was the default the system '
                  'applied (pre-accepted silent corrections).')
    decided_at = models.DateTimeField(null=True, blank=True)
    applied = models.BooleanField(
        default=False,
        help_text='Whether this correction has been written to the list '
                  'item.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['row_number', 'id']
        indexes = [
            models.Index(fields=['run', 'row_number'],
                         name='api_lcs_run_row_idx'),
        ]

    def __str__(self):
        return (f'{self.kind} {self.code} on row {self.row_number} '
                f'(run {self.run_id})')

    @property
    def final_value(self):
        if self.decision == self.EDITED:
            return self.decided_value
        return self.corrected_value
