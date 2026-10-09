import uuid
from simple_history.models import HistoricalRecords
from django.db import models
from django.db.models import Q
from api.constants import OriginSource


class FacilityAlias(models.Model):
    """
    Links the OS ID of a no longer existing Facility to another Facility,
    or records that the OS ID was retired and points nowhere.

    A MERGE or DELETE alias is a redirect: ``facility`` is the row that
    now answers for ``os_id``. A NOT_A_FACILITY alias is a terminal
    tombstone: ``facility`` is NULL, and the row keeps the detection key
    ``(retired_source, retired_external_id)`` and the vote tally that
    retired the candidate so ingest can refuse to re-create it and the
    public API can answer 410 Gone (OSDEV-3246).
    """
    class Meta:
        verbose_name_plural = "facility aliases"
        indexes = [
            # Ingest looks a detection up by its source key before
            # creating a candidate. Partial: only tombstones carry the
            # key, so redirect rows never enter the index.
            models.Index(
                fields=['retired_source', 'retired_external_id'],
                condition=Q(retired_external_id__isnull=False),
                name='api_facilityalias_retired_idx',
            ),
        ]

    MERGE = 'MERGE'
    DELETE = 'DELETE'
    NOT_A_FACILITY = 'NOT_A_FACILITY'

    REASON_CHOICES = (
        (MERGE, MERGE),
        (DELETE, DELETE),
        (NOT_A_FACILITY, NOT_A_FACILITY),
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the facility alias.'
    )
    os_id = models.CharField(
        max_length=32,
        primary_key=True,
        editable=False,
        help_text=('The OS ID of a no longer existent Facility which '
                   'should be redirected to a different Facility.'))
    facility = models.ForeignKey(
        'Facility',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text=('The facility now associated with the os_id. NULL '
                   'when the OS ID was retired (reason NOT_A_FACILITY) '
                   'and redirects nowhere.')
    )
    reason = models.CharField(
        null=False,
        max_length=14,
        choices=REASON_CHOICES,
        help_text='The reason why this alias was created'
    )
    retired_source = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text=('For a NOT_A_FACILITY tombstone, the detection source '
                   'of the retired candidate (copied from '
                   'Facility.source), so ingest can suppress re-creation.')
    )
    retired_external_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text=('For a NOT_A_FACILITY tombstone, the identifier of the '
                   'retired candidate in its detection source (copied '
                   'from Facility.external_id).')
    )
    retirement_tally = models.JSONField(
        null=True,
        blank=True,
        help_text=('For a NOT_A_FACILITY tombstone, the final community '
                   'vote tally that retired the candidate, e.g. '
                   '{"confirmed": 1, "not_a_facility": 5, '
                   '"retired_at": "<ISO 8601>", "retired_by": <user id>}.')
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(
        excluded_fields=['uuid', 'origin_source']
    )

    @property
    def is_tombstone(self):
        """True when this alias retires its OS ID instead of redirecting."""
        return (
            self.facility_id is None
            and self.reason == FacilityAlias.NOT_A_FACILITY
        )

    def __str__(self):
        if self.facility_id is None:
            return f'{self.os_id} -> retired ({self.reason})'
        return f'{self.os_id} -> {self.facility}'
