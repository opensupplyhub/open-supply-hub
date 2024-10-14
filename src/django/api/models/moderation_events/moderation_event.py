from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.api.models.facility.facility_list_item import FacilityListItem


class ModerationQueue(models.Model):
    '''
    Data that is needed for Moderation Queue.
    '''

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Date when the moderation queue entry was created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Date when the moderation queue entry was last updated.'
    )
    moderation_decision_date = models.DateTimeField(
        auto_now=True,
        help_text='Date when the moderation decision was made.'
    )

    production_location_list_item = models.OneToOneField(
        FacilityListItem,
        on_delete=models.CASCADE,
        related_name='moderation_queue',
        help_text='Linked facility list item for this moderation queue entry.'
    )

    raw_json = models.JSONField(
        null=False,
        blank=False,
        default=dict,
        help_text=(
            'Key-value pairs of the parsed row and '
            'header for the moderation data.'
        )
    )

    MATCHED = 'MATCHED'
    NEW_LOCATION = 'NEW_LOCATION'
    POTENTIAL_MATCH = 'POTENTIAL_MATCH'

    MATCH_STATUS_CHOICES = [
        (MATCHED, 'Matched'),
        (NEW_LOCATION, 'New Location'),
        (POTENTIAL_MATCH, 'Potential Match'),
    ]

    match_status = models.CharField(
        max_length=200,
        null=True,
        choices=MATCH_STATUS_CHOICES,
        help_text='Match status of the production location.'
    )

    APPROVED = 'APPROVED'
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'
    REVOKED = 'REVOKED'

    MODERATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (REVOKED, 'Revoked'),
    ]

    moderation_status = models.CharField(
        max_length=200,
        choices=MODERATION_STATUS_CHOICES,
        default=PENDING,
        help_text='Moderation status of the production location.'
    )

    record_type = ArrayField(
        models.CharField(max_length=200, null=True),
        help_text='List of record types for the production location.',
        blank=True
    )

    def __str__(self):
        return (
            'ModerationQueue entry for ' +
            str(self.production_location_list_item) +
            ' with status ' +
            self.moderation_status
        )
