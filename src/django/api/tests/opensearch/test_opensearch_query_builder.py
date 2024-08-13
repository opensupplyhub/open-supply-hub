import logging

from opensearchpy import OpenSearch
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder
from .opensearch_test_case import OpenSearchIntegrationTestCase

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


class OpenSearchQueryBuilderTest(OpenSearchIntegrationTestCase):

    def test_query_builder(self):
        self.client: OpenSearch = self.getClient()
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
        self.client.index(index=self.index_name, body=doc, id=self.client.count())
        self.client.indices.refresh(index=self.index_name)

        # Search match for the document
        builder_match = OpenSearchQueryBuilder()
        builder_match.add_match('name', '', fuzziness=1)

        response_match = self.client.search(index=self.index_name, body=builder_match.get_final_query_body())
        self.assertEqual(response_match['hits']['total']['value'], 0)

        # Search multi match for the document
        builder_multi_match = OpenSearchQueryBuilder()
        builder_multi_match.add_multi_match('NINGBO')

        response_multi_match = self.client.search(index=self.index_name, body=builder_multi_match.get_final_query_body())
        self.assertGreater(response_multi_match['hits']['total']['value'], 0)

        # Search terms for the document
        builder_terms = OpenSearchQueryBuilder()
        builder_terms.add_terms('country', ['US', 'CN'])

        response_terms = self.client.search(index=self.index_name, body=builder_terms.get_final_query_body())
        self.assertGreater(response_terms['hits']['total']['value'], 0)
