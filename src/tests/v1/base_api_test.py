import os
from opensearch.opensearch_test_case \
    import OpenSearchIntegrationTestCase


class BaseAPITest(OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.open_search_client = self.getClient()

        host = os.getenv('REACT_HOST')
        port = os.getenv('REACT_PORT')
        token = os.getenv('USER_API_TOKEN')

        self.root_url = f"http://{host}:{port}"

        self.basic_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}',
            'Host': f'localhost:{port}'
        }
