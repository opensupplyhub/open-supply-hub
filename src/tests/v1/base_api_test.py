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
