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
    
    def getClient(self) -> OpenSearch:
        return self.__client
