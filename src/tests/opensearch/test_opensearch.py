from opensearchpy import OpenSearch
from .opensearch_test_case import OpenSearchIntegrationTestCase


class OpenSearchTest(OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.client: OpenSearch = self.getClient()

    def test_connection(self):
        health = self.client.cluster.health()
        self.assertIn(health['status'], ['green', 'yellow'])

    def test_create_and_index_document(self):
        doc = {'title': 'Test Document'}
        response = self.client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.client.count()
        )
        self.assertEqual(response['result'], 'created')

    def test_search_document(self):
        # Index a document
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "NO.11 DONGQIAN LAKE AREA,YINXIAN AVENUE,NINGBO,CHINA",
            "name": "NINGBO HUAYI GARMENTS CO LTD",
            "country": {
                "alpha_2": "CN"
            },
            "os_id": "CN2024221G4W0WA",
            "coordinates": {
                "lon": 121.5504069,
                "lat": 29.8194363
            },
            "claim_status": "unclaimed"
        }
        self.client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.client.count()
        )
        self.client.indices.refresh(index=self.production_locations_index_name)

        # Search for the document
        query = {
            'query': {
                'match': {
                    'name': 'HUAYI'
                }
            }
        }
        response = self.client.search(
            index=self.production_locations_index_name,
            body=query
        )
        self.assertGreater(response['hits']['total']['value'], 0)
