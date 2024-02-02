from json import dumps as stringify
from logging import getLogger

from django.db import models

logger = getLogger(__name__)


class ContributorWebhook(models.Model):
    """
    Contains webhook settings for contributor notifications
    """

    # These must be kept in sync with the identical list in constants.js
    ALL_FACILITIES = "ALL_FACILITIES"
    ASSOCIATED = "ASSOCIATED"

    NOTIFICATION_TYPES = [
        (ALL_FACILITIES, ALL_FACILITIES),
        (ASSOCIATED, ASSOCIATED),
    ]

    # Statuses for logging notification delivery
    SKIPPED = "SKIPPED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor who configured this webhook.'
    )
    url = models.URLField(
        null=False,
        blank=False,
        help_text='The URL of the web hook'
    )
    notification_type = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        choices=NOTIFICATION_TYPES,
        help_text=('Whether to send notifications for all events '
                   'or only events for associated facilities.')
    )
    filter_query_string = models.TextField(
        null=False,
        blank=True,
        default='',
        help_text=('A query string search filter that will be applied before '
                   'sending notification events')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def log_event(self, event, status):
        detail = {
          "event_id": event.pk,
          "webhook_id": self.pk,
          "contributor_id": self.contributor_id,
          "status": status,
          "event_time": event.event_time.isoformat()
        }
        logger.info("ContributorWebhook %s: %s", status, stringify(detail))
