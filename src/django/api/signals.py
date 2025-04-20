import logging
import json

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from opensearchpy.exceptions import ConnectionError

from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from oar.rollbar import report_error_to_rollbar
from api.views.v1.index_names import OpenSearchIndexNames


log = logging.getLogger(__name__)


def signal_error_notifier(error_log_message, response):
    log.error(error_log_message)
    report_error_to_rollbar(
        message=error_log_message,
        extra_data={
            'response_result': json.dumps(response),
        }
    )


@receiver(post_delete, sender=Facility)
def location_post_delete_handler_for_opensearch(instance, **kwargs):
    opensearch = OpenSearchServiceConnection()
    try:
        response = opensearch.client.delete(
            index=OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            id=instance.id,
        )
    except ConnectionError:
        log.error(
            '[Location Deletion] Lost connection to OpenSearch cluster.'
        )
        raise

    if response and response.get('result') == 'not_found':
        error_log_message = (
            "[Location Deletion] Facility not found "
            "in OpenSearch, indicating "
            "data inconsistency."
        )
        signal_error_notifier(error_log_message, response)


@receiver(post_save, sender=ModerationEvent)
def moderation_event_update_handler_for_opensearch(
    instance,
    created,
    **kwargs
):
    if created:
        return

    opensearch = OpenSearchServiceConnection()
    
    contributor_email = None
    if instance.contributor and instance.contributor.admin:
        contributor_email = instance.contributor.admin.email
    
    try:
        response = opensearch.client.update(
            index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            id=str(instance.uuid),
            body={
                "doc": {
                    "uuid": str(instance.uuid),
                    "status": str(instance.status),
                    "os": instance.os.id if instance.os else None,
                    "contributor_email": contributor_email
                }
            },
        )
    except ConnectionError:
        log.error(
            "[Moderation Event Updating] "
            "Lost connection to OpenSearch cluster."
        )
        raise

    if response and response.get('result') == 'not_found':
        error_log_message = (
            "[Moderation Event Updating] "
            "ModerationEvent not found in OpenSearch, "
            "indicating data inconsistency."
        )
        signal_error_notifier(error_log_message, response)
