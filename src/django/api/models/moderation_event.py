import uuid
from django.db import models
from api.models.facility.facility_list_item import FacilityListItem


class ModerationEvent(models.Model):
    '''
    Data that is needed for moderation queue.
    '''
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
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
        help_text='Date when the moderation decision was made.'
    )

    production_location_list_item = models.OneToOneField(
        FacilityListItem,
        on_delete=models.CASCADE,
        related_name='moderation_queue',
        help_text='Linked facility list item for this moderation queue entry.'
    )

    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    CLAIM = 'CLAIM'

    REQUEST_TYPE_CHOICES = [
        (CREATE, 'Create'),
        (UPDATE, 'Update'),
        (CLAIM, 'Claim'),
    ]

    request_type = models.CharField(
        max_length=200,
        null=False,
        choices=REQUEST_TYPE_CHOICES,
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

    PENDING = 'PENDING'
    RESOLVED = 'RESOLVED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (RESOLVED, 'Resolved'),
    ]

    status = models.CharField(
        max_length=200,
        choices=STATUS_CHOICES,
        default=PENDING,
        null=False,
        help_text='Moderation status of the production location.'
    )

    API = 'API'
    SLC = 'SLC'

    SOURCE_CHOICES = [
        (API, 'API'),
        (SLC, 'SLC'),
    ]

    source = models.CharField(
        max_length=200,
        choices=SOURCE_CHOICES,
        blank=False,
        null=False,
        help_text='Source type of production location.'
    )

    def __str__(self):
        return (
            'ModerationQueue entry for ' +
            str(self.production_location_list_item) +
            ' with status ' +
            self.status
        )
