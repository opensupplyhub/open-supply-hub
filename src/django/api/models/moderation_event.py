import uuid
from django.db import models
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_claim import FacilityClaim


class ModerationEvent(models.Model):
    '''
    Data that is needed for moderation queue.
    '''
    class RequestType(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        CLAIM = 'CLAIM', 'Claim'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    class Source(models.TextChoices):
        API = 'API', 'API'
        SLC = 'SLC', 'SLC'

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text=(
            'Unique identifier to make moderation '
            'event table more reusable across the app.'
        )
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Date when the moderation queue entry was created.'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Date when the moderation queue entry was last updated.',
        db_index=True
    )

    status_change_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date when the moderation decision was made.'
    )

    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.PROTECT,
        null=True,
        related_name='moderation_event_contributor',
        help_text='Linked contributor responsible for this moderation event.'
    )

    os = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderation_event_os',
        help_text='Linked facility OS ID for this moderation event.'
    )

    claim = models.OneToOneField(
        FacilityClaim,
        on_delete=models.SET_NULL,
        null=True,
        related_name='moderation_event_claim',
        help_text='Linked claim id for this production location.'
    )

    request_type = models.CharField(
        max_length=6,
        null=False,
        choices=RequestType.choices,
        help_text='Type of moderation record.'
    )

    raw_data = models.JSONField(
        null=False,
        blank=False,
        default=dict,
        help_text=(
            'Key-value pairs of the non-parsed row and '
            'header for the moderation data.'
        )
    )

    cleaned_data = models.JSONField(
        null=False,
        blank=False,
        default=dict,
        help_text=(
            'Key-value pairs of the parsed row and '
            'header for the moderation data.'
        )
    )

    geocode_result = models.JSONField(
        null=False,
        blank=False,
        default=dict,
        help_text=(
            'Result of the geocode operation.'
        )
    )

    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.PENDING,
        null=False,
        help_text='Moderation status of the production location.'
    )

    source = models.CharField(
        max_length=3,
        choices=Source.choices,
        blank=True,
        default='',
        help_text=(
            'Source type of production location.'
            ' If request_type is CLAIM, no source type.'
        )
    )

    def __str__(self):
        return (
            f'ModerationEvent entry {self.uuid} '
            f'with request type {self.request_type} '
            f'and status {self.status}'
        )
