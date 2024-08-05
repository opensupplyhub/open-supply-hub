import logging
from api.services.opensearch import OpenSearchServiceConnection
from api.services.search_interface import SearchInterface
from opensearchpy.exceptions import OpenSearchException

logger = logging.getLogger(__name__)


class OpenSearchServiceException(Exception):
    def __init__(
        self,
        message="An unexpected error occurred while processing the request."
    ):
        self.message = message
        super().__init__(self.message)


class OpenSearchService(SearchInterface):
    def __init__(self):
        self.__client = OpenSearchServiceConnection().client

    def search_production_locations(self, index_name, query_body):
        try:
            response = self.__client.search(
                body=query_body,
                index=index_name
            )
            return response
        except OpenSearchException as e:
            logger.error(f"An error occurred while \
                            searching in index '{index_name}': {e}")
            raise OpenSearchServiceException()
