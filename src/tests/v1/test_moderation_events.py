import requests
from .base_api_test \
    import BaseAPITest


class ModerationEventsTest(BaseAPITest):

    def test_production_locations_status(self):
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/",
            headers=self.basic_headers,
        )
        self.assertEqual(response.status_code, 200)

