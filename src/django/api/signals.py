import logging
import json

from django.db.models.signals import post_delete
from django.dispatch import receiver
from opensearchpy.exceptions import ConnectionError

from api.models.facility.facility import Facility
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from oar.rollbar import report_error_to_rollbar
from api.views.v1.index_names import OpenSearchIndexNames


log = logging.getLogger(__name__)


@receiver(post_delete, sender=Facility)
def location_post_delete_handler_for_opensearch(sender, **kwargs):
    opensearch = OpenSearchServiceConnection()
    location_instance = kwargs.get('instance')
    try:
        response = opensearch.client.delete(
            index=OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            id=location_instance.id
        )
    except ConnectionError:
        log.error(('[Location Deletion] The Django app lost the connection '
                   'with the OpenSearch cluster.'))
        raise

    if (response and response.get('result') == 'not_found'):
        log.error(("[Location Deletion] The same location wasn't found in the "
                   'OpenSearch data store, indicating critical data '
                   'inconsistency.'))
        report_error_to_rollbar(
            message=(
                "[Location Deletion] The same location wasn't found in the "
                'OpenSearch data store, indicating critical data '
                'inconsistency.'
            ),
            extra_data={
                'response_result': json.dumps(response),
            }
        )
