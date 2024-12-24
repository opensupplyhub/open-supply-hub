import requests
import uuid
from datetime import datetime
from ..base_api_test \
    import BaseAPITest
class ModerationEventRecordTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.timeout = 5
        self.moderation_event_id = None
        self.potential_match_os_id = None
        self.name = 'Changzhou Hualida Garments Group Co.'
        self.address = 'Lot 303 No.1108 Zhongwu High Road Changzhou Jiangsu China - China'
        self.county_alpha_2_code = 'CN'

        self.new_moderation_event = {
            'source': 'API',
            'name': self.name,
            'address': self.address,
            'country': 'China',
            'sector': [
                'Apparel'
            ],
            'coordinates': {
                'lat': 31.750302,
                'lng': 119.96891
            }
        }

    def test_moderation_events_default_output(self):
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(len(result['data']), 10)

    def test_moderation_events_exact(self):
        moderation_id = '1f35a90f-70a0-4c3e-8e06-2ed8e1fc6800'
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{moderation_id}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(result['moderation_id'], moderation_id)

    def test_moderation_events_confirmation(self):
        # 1. Creates a new moderation event for the production location creation with the given details. ( POST /v1/production-locations/ )
        response = requests.post(
            f"{self.root_url}/api/v1/production-locations/",
            headers=self.basic_headers,
            json=self.new_moderation_event,
        )
        result = response.json()
        print(f'@@@ Result of created moderation event {result}')

        self.assertEqual(len(result), 3, "Response JSON does not have exactly 3 items.")
        expected_keys = {'moderation_id', 'moderation_status', 'created_at'}
        self.assertEqual(set(result.keys()), expected_keys, "Response JSON keys do not match expected keys.")

        try:
            uuid_obj = uuid.UUID(result['moderation_id'])
            self.assertEqual(str(uuid_obj), result['moderation_id'], "moderation_id is not a valid UUID.")
        except ValueError:
            self.fail("moderation_id is not a valid UUID.")

        self.assertEqual(result['moderation_status'], 'PENDING', "moderation_status is not 'PENDING'.")

        try:
            datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))  # Handle 'Z' for UTC
        except ValueError:
            self.fail("created_at is not a valid ISO 8601 date.")

        self.moderation_event_id = result['moderation_id']
        print(f'[Contribution Record; moderation id:] {self.moderation_event_id}')

        # 2. Creates a multiple moderation events that will act as potential matches. ( POST /v1/production-locations/ )
        HTTP_202_ACCEPTED = 202
        for i in range(5):
            with self.subTest(i=i):  # Subtest for better diagnostics
                response = requests.post(
                    f"{self.root_url}/api/v1/production-locations/",
                    headers=self.basic_headers,
                    json=self.new_moderation_event
                )

                self.assertEqual(response.status_code, HTTP_202_ACCEPTED, f"Unexpected status code: {response.status_code}")

        # 3. Show potential matches for moderation event that has been created first ( GET /v1/production-locations/?name={name}&country={county_alpha_2_code}&address={address}/ )
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?name={self.name}&country={self.county_alpha_2_code}&address={self.address}/",
            headers=self.basic_headers,
            timeout=self.timeout
        )
        result = response.json()
        self.assertGreater(len(result['data']), 1)
        self.potential_match_os_id = result['data'][0]['os_id']
        print(f'[Contribution Record; first potential match OS ID:] {self.potential_match_os_id}')

        # 4. Confirm potential match ( PATCH /v1/moderation-events/{moderation_id}/production-locations/{os_id}/ )
        self.assertIsNotNone(self.moderation_event_id, "moderation_event_id is not set. Ensure the moderation event is created first.")
        self.assertIsNotNone(self.potential_match_os_id, "potential_match_os_id is not set. Ensure that potential match OS ID is available.")

        HTTP_200_OK = 200
        response = requests.patch(
            f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}/production-locations/{self.potential_match_os_id}/",
            headers=self.basic_headers,
            timeout=self.timeout
        )
        result = response.json()
        print(result)
        self.assertEqual(response.status_code, HTTP_200_OK, f"Unexpected status code: {response.status_code}")
        expected_keys = {'os_id'}
        self.assertEqual(set(result.keys()), expected_keys, "Response JSON keys do not match expected keys.")
