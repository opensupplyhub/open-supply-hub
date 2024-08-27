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
    def __init__(self, client=None):
        self.__client = client or OpenSearchServiceConnection().client

    def __rename_lon_field(self, source):
        coordinates = source.get('coordinates')
        if not coordinates:
            return source
        else:
            coordinates['lng'] = coordinates.pop("lon")
            return source

    def __prepare_opensearch_response(self, response):
        if not response or "hits" not in response:
            logger.error(f"Invalid response format: {response}")
            raise OpenSearchServiceException(
                "Invalid response format from OpenSearch."
                )

        total_hits = response.get("hits", {}).get("total", {}).get("value", 0)
        hits = response.get("hits", {}).get("hits", [])

        data = []
        for hit in hits:
            if "_source" in hit:
                data.append(self.__rename_lon_field(hit["_source"]))
            else:
                logger.warning(f"Missing '_source' in hit: {hit}")

        return {
            "count": total_hits,
            "data": data
        }

    def search_index(self, index_name, query_body):
        try:
            response = self.__client.search(body=query_body, index=index_name)
            return self.__prepare_opensearch_response(response)

        except OpenSearchException as e:
            logger.error(f"An error occurred while searching in \
                          index '{index_name}': {e}")
            raise OpenSearchServiceException()
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise OpenSearchServiceException()
