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

        self.index_name = os.getenv('OPENSEARCH_INDEX_NAME')

    def getClient(self) -> OpenSearch:
        return self.__client
