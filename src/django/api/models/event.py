from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from api.constants import FacilityHistoryActions


class Event(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['content_type', 'object_id'],
                name='api_event_content_object_idx',
            ),
        ]

    EVENT_TYPE_CHOICES = (
        (FacilityHistoryActions.CREATE, FacilityHistoryActions.CREATE),
        (FacilityHistoryActions.UPDATE, FacilityHistoryActions.UPDATE),
        (FacilityHistoryActions.DELETE, FacilityHistoryActions.DELETE),
        (FacilityHistoryActions.MERGE, FacilityHistoryActions.MERGE),
        (FacilityHistoryActions.SPLIT, FacilityHistoryActions.SPLIT),
        (FacilityHistoryActions.MOVE, FacilityHistoryActions.MOVE),
        (FacilityHistoryActions.OTHER, FacilityHistoryActions.OTHER),
        (FacilityHistoryActions.ASSOCIATE, FacilityHistoryActions.ASSOCIATE),
        (FacilityHistoryActions.DISSOCIATE, FacilityHistoryActions.DISSOCIATE),
        (FacilityHistoryActions.CLAIM, FacilityHistoryActions.CLAIM),
        (FacilityHistoryActions.CLAIM_UPDATE,
         FacilityHistoryActions.CLAIM_UPDATE),
        (FacilityHistoryActions.CLAIM_REVOKE,
         FacilityHistoryActions.CLAIM_REVOKE),
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        help_text='The type of the object for which the event occurred. ' +
        'Set automatically by passing the object to the content_object ' +
        'field.')
    object_id = models.CharField(
        max_length=32,
        help_text='The ID of the object for which the event occurred. ' +
        'Set automatically by passing the object to the content_object ' +
        'field.')
    content_object = GenericForeignKey('content_type', 'object_id')
    event_type = models.CharField(
        max_length=50, choices=EVENT_TYPE_CHOICES,
        help_text='The type of the event, e.g. CLAIM or DELETE.')
    event_time = models.DateTimeField(
        help_text='The time when the event occurred.')
    event_details = models.JSONField(
        help_text='Additional information about the event.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = self.content_type.name
        return (f"{content_type} ({self.object_id}) - "
                f"{self.event_type} ({self.id})")
