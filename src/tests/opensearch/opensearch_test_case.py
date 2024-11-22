import os
import unittest
from opensearchpy import OpenSearch, RequestsHttpConnection


class OpenSearchIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        host = os.getenv('OPENSEARCH_HOST')
        port = os.getenv('OPENSEARCH_PORT')

        self.__client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=None,
            connection_class=RequestsHttpConnection,
        )

        self.moderation_events_index_name = os.getenv('OPENSEARCH_MODERATION_EVENTS_INDEX')
        self.production_locations_index_name = os.getenv('OPENSEARCH_PRODUCTION_LOCATIONS_INDEX')

    def getClient(self) -> OpenSearch:
        return self.__client
