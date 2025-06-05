from simple_history.models import HistoricalRecords
from django.db import models


class FacilityActivityReport(models.Model):
    """
    Report a facility as closed or reopened.
    """
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    CLOSURE_STATES = ((OPEN, OPEN), (CLOSED, CLOSED))

    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (CONFIRMED, CONFIRMED),
        (REJECTED, REJECTED))

    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.CASCADE,
        help_text='The facility to which this report applies.'
    )
    reported_by_user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='reported by user',
        help_text='The user who reported the change.',
        related_name='reporter_of_activity'
    )
    reported_by_contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='reported by contributor',
        help_text='The contributor who reported the change.'
    )
    reason_for_report = models.TextField(
        null=True,
        blank=True,
        verbose_name='reason for report',
        help_text=('The reason for requesting this status change.'))
    closure_state = models.CharField(
        max_length=6,
        null=False,
        blank=False,
        choices=CLOSURE_STATES,
        verbose_name='closure state',
        help_text='Whether the facility is open or closed.')
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the report was approved, if applicable.')
    status = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text='The current status of the report.')
    status_change_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='status change reason',
        help_text=('The reason entered when changing '
                   'the status of this report.'))
    status_change_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='status changed by',
        help_text='The user who changed the status of this report',
        related_name='changer_of_status')
    status_change_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='status change date',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_by_contributor_uuid = models.ForeignKey(
        'Contributor',
        to_field='uuid',
        db_column='reported_by_contributor_uuid',
        on_delete=models.PROTECT,
        null=False,
        editable=False,
        related_name='facility_activity_reports',
        help_text='The UUID of the contributor who reported the change.'
    )

    history = HistoricalRecords()

    def __str__(self):
        return ('FacilityActivityReport {id} - Facility {facility_id}, '
                'Closure State: {closure_state}, '
                'Status: {status} '
                ).format(**self.__dict__)
