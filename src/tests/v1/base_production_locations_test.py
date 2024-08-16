import os
from opensearch.opensearch_test_case \
    import OpenSearchIntegrationTestCase


class BaseProductionLocationsTest(OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.open_search_client= self.getClient()

        host = os.getenv('REACT_HOST')
        port = os.getenv('REACT_PORT')
        self.root_url = f"http://{host}:{port}"

        self.basic_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token 1d18b962d6f976b0b7e8fcf9fcc39b56cf278051',
            'Host': "localhost:6543"
        }
