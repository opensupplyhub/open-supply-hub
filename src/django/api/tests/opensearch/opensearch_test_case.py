import os
from django.test import TestCase
from opensearchpy import OpenSearch, RequestsHttpConnection

from api.views.v1.index_names import OpenSearchIndexNames

class OpenSearchIntegrationTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        host = os.getenv('OPENSEARCH_HOST')
        port = os.getenv('OPENSEARCH_PORT')

        cls.__client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=None,
            connection_class=RequestsHttpConnection,
        )

        cls.index_name = OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX
    
    def setUp(self):
        # Ensure the index is created before each test
        self.__client.indices.create(index=self.index_name, ignore=400)
    
    def tearDown(self):
        # Delete the index after each test
        self.__client.indices.delete(index=self.index_name, ignore=[400, 404])
    
    def getClient(self) -> OpenSearch:
        return self.__client

