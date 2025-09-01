import logging
import json

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from opensearchpy.exceptions import \
    ConnectionError, NotFoundError, AuthorizationException

from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.extended_field import ExtendedField
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_activity_report import FacilityActivityReport
from api.models.facility.facility_location import FacilityLocation
from api.models.facility.facility_alias import FacilityAlias
from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
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
    try:
        response = opensearch.client.update(
            index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            id=str(instance.uuid),
            body={
                "doc": {
                    "uuid": str(instance.uuid),
                    "status": str(instance.status),
                    "os": instance.os.id if instance.os else None
                }
            },
        )
    except ConnectionError:
        log.error(
            "[Moderation Event Updating] "
            "Lost connection to OpenSearch cluster."
        )
        raise
    except NotFoundError:
        log.error(
            "[Moderation Event Updating] "
            "ModerationEvent not found in OpenSearch."
        )
        return
    except AuthorizationException:
        log.error(
            "[Moderation Event Updating] "
            "Authorization error when accessing OpenSearch."
        )
        return

    if response and response.get('result') == 'not_found':
        error_log_message = (
            "[Moderation Event Updating] "
            "ModerationEvent not found in OpenSearch, "
            "indicating data inconsistency."
        )
        signal_error_notifier(error_log_message, response)


def set_origin_source_on_create(instance, created, **kwargs):
    if created and instance.origin_source is None:
        instance.origin_source = settings.INSTANCE_SOURCE
        instance.save(update_fields=['origin_source'])


for model in [
    FacilityListItem,
    ExtendedField,
    FacilityClaim,
    FacilityAlias,
    FacilityActivityReport,
    FacilityLocation
]:
    post_save.connect(set_origin_source_on_create, sender=model)


@receiver(post_save, sender=Contributor)
def sync_user_flag_with_contributor_verification(instance, **kwargs):
    try:
        user = instance.admin
        if not instance.is_verified:
            if user.can_partially_update_production_location:
                User.objects.filter(pk=user.pk).update(
                    can_partially_update_production_location=False
                )
    except Exception as exc:
        log.error(
            '[User field update] Failed to sync user partial update flag with '
            f'contributor verification change: {exc}'
        )
