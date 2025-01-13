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

@receiver(post_save, sender=Facility)
def location_post_save_handler_for_opensearch(instance, created, **kwargs):
    opensearch = OpenSearchServiceConnection()

    try:
        if created:
            # Index a new facility in OpenSearch
            response = opensearch.client.index(
                index=OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
                id=instance.id,
                body={
                    "name": instance.name,
                    "address": instance.address,
                    "country": instance.country,
                    "coordinates": instance.coordinates,
                    "number_of_workers": instance.number_of_workers,
                    "sector": instance.sector,
                    "parent_company": instance.parent_company,
                    "product_type": instance.product_type,
                    "location_type": instance.location_type,
                    "processing_type": instance.processing_type,
                    "minimum_order_quantity": instance.minimum_order_quantity,
                    "average_lead_time": instance.average_lead_time,
                    "percent_female_workers": instance.percent_female_workers,
                    "affiliations": instance.affiliations,
                    "certifications_standards_regulations": instance.certifications_standards_regulations,
                    "claim_status": instance.claim_status,
                },
            )
        else:
            # Update an existing facility in OpenSearch
            response = opensearch.client.update(
                index=OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
                id=instance.id,
                body={
                    "doc": {
                        "name": instance.name,
                        "address": instance.address,
                        "country": instance.country,
                        "coordinates": instance.coordinates,
                        "number_of_workers": instance.number_of_workers,
                        "sector": instance.sector,
                        "parent_company": instance.parent_company,
                        "product_type": instance.product_type,
                        "location_type": instance.location_type,
                        "processing_type": instance.processing_type,
                        "minimum_order_quantity": instance.minimum_order_quantity,
                        "average_lead_time": instance.average_lead_time,
                        "percent_female_workers": instance.percent_female_workers,
                        "affiliations": instance.affiliations,
                        "certifications_standards_regulations": instance.certifications_standards_regulations,
                        "claim_status": instance.claim_status,
                    }
                },
            )
    except ConnectionError:
        log.error(
            "[Location Save] Lost connection to OpenSearch cluster."
        )
        raise

    if response and response.get('result') == 'not_found':
        error_log_message = (
            "[Location Save] Facility not found in OpenSearch, indicating "
            "data inconsistency."
        )
        signal_error_notifier(error_log_message, response)

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
            "[Location Deletion] Facility not found in OpenSearch, indicating "
            "data inconsistency."
        )
        signal_error_notifier(error_log_message, response)
