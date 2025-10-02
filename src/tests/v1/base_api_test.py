import os
from opensearch.opensearch_test_case \
    import OpenSearchIntegrationTestCase


class BaseAPITest(OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.open_search_client = self.getClient()

        self.host = os.getenv('REACT_HOST')
        self.port = os.getenv('REACT_PORT')
        self.admin_token = os.getenv('ADMIN_API_TOKEN')
        self.user_token = os.getenv('USER_API_TOKEN')

        self.root_url = f"http://{self.host}:{self.port}"

        self.basic_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.admin_token}',
            'Host': f'localhost:{self.port}'
        }

        # Ensure index exists with correct mappings for geo queries and country fields.
        idx = os.getenv('OPENSEARCH_PRODUCTION_LOCATIONS_INDEX') or 'production-locations'
        self.open_search_client.indices.delete(index=idx, ignore=[404])
        self.open_search_client.indices.create(
            index=idx,
            body={
                "mappings": {
                    "properties": {
                        "coordinates": {"type": "geo_point"},
                        "country": {
                            "properties": {
                                "name": {"type": "keyword"},
                                "alpha_2": {"type": "keyword"},
                                "alpha_3": {"type": "keyword"},
                                "numeric": {"type": "keyword"},
                            }
                        }
                    }
                }
            }
        )

        # Seed a deterministic document:
        # - includes 'country' so the country test never KeyErrors
        # - coordinates match a vertex used by the large geo polygon test (lat=60.0, lon=41.0)
        seed_doc = {
            "os_id": "SEED_OS_ID",
            "name": "AAA Seed Country Doc",
            "country": {
                "name": "United States",
                "alpha_2": "US",
                "alpha_3": "USA",
                "numeric": "840"
            },
            "coordinates": {"lat": 60.0, "lon": 41.0},
            "address": "Seed Address",
            "sector": ["Seed"],
            "claim_status": "unclaimed"
        }
        self.open_search_client.index(index=idx, body=seed_doc, id="seed-country-geo-doc")
        self.open_search_client.indices.refresh(index=idx)