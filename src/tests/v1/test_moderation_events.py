import requests
from .base_api_test \
    import BaseAPITest


class ModerationEventsTest(BaseAPITest):

    def test_moderation_events_exact(self):
        moderation_id_wrong = '0f35a90f-70a0-4c3e-8e06-2ed8e1fc6800'
        response = requests.get(
                f"{self.root_url}/api/v1/moderation-events/{moderation_id_wrong}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['count'], 0)

        moderation_id = '1f35a90f-70a0-4c3e-8e06-2ed8e1fc6800'
        response = requests.get(
                f"{self.root_url}/api/v1/moderation-events/{moderation_id}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['data'][0]['moderation_id'], moderation_id)
