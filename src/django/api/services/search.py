import logging
from .opensearch import OpenSearchServiceConnection
from .search_interface import SearchInterface
from opensearchpy.exceptions import OpenSearchException

logger = logging.getLogger(__name__)


class OpenSearchService(SearchInterface):
    def __init__(self):
        self.__client = OpenSearchServiceConnection().client

    def search_production_locations(self, query_body):
        index_name = 'production-locations'
        try:
            response = self.__client.search(
                body=query_body,
                index=index_name
            )
            return response
        except OpenSearchException as e:
            logger.error(f"An error occurred while \
                         searching in index '{index_name}': {e}")
            return None
