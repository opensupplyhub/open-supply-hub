import requests
import uuid
import time
from datetime import datetime
from ..base_api_test \
    import BaseAPITest

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_429_TOO_MANY_REQUEST = 429
REINDEX_INTERVAL = 80


class ModerationEventRecordTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.moderation_event_id = None
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

        self.potential_match_facility = {
            'name': self.name,
            'address': self.address,
            'country': 'China',
            'sector': 'Apparel',
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

    def create_moderation_event(self):
        response = requests.post(
            f"{self.root_url}/api/v1/production-locations/",
            headers=self.basic_headers,
            json=self.new_moderation_event,
        )
        result = response.json()

        self.assertEqual(len(result), 3, "Response JSON does not have exactly 3 items.")
        expected_keys = {'moderation_id', 'moderation_status', 'created_at'}
        self.assertEqual(set(result.keys()), expected_keys, "Response JSON keys do not match expected keys.")

        try:
            uuid_obj = uuid.UUID(result['moderation_id'])
            self.assertEqual(str(uuid_obj), result['moderation_id'], "moderation_id is not a valid UUID.")
        except ValueError:
            self.fail("moderation_id is not a valid UUID.")

        self.assertEqual(result['moderation_status'], 'PENDING', "moderation_status is not 'PENDING'.")
        self.moderation_event_id = result['moderation_id']
        print(f'[Contribution Record]; moderation id: {self.moderation_event_id}')
        # Wait till the newly created facilities be indexed in the OpenSearch
        time.sleep(REINDEX_INTERVAL)

    def test_moderation_events_confirmation(self):
        # 1. Creates a new moderation event for the production location creation with the given details. ( POST /v1/production-locations/ )
        self.create_moderation_event()

        # 2. Creates a multiple facilities that will act as potential matches. ( POST /facilities/ )
        for i in range(5):
            with self.subTest(i=i): # Subtest for better diagnostics
                response = requests.post(
                    f"{self.root_url}/api/facilities/",
                    headers=self.basic_headers,
                    json=self.potential_match_facility
                )

                self.assertEqual(response.status_code, HTTP_201_CREATED, f"Unexpected status code: {response.status_code}")

        # 3. Show potential matches for moderation event that has been created first ( GET /v1/production-locations/?name={name}&country={county_alpha_2_code}&address={address}/ )
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?name={self.name}&country={self.county_alpha_2_code}&address={self.address}/",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertGreater(len(result['data']), 1)
        potential_match_os_id = result['data'][0]['os_id']
        print(f'[Contribution Record]; first potential match OS ID: {potential_match_os_id}')

        # 4. Confirm potential match ( PATCH /v1/moderation-events/{moderation_id}/production-locations/{os_id}/ )
        self.assertIsNotNone(self.moderation_event_id, "moderation_event_id is not set. Ensure the moderation event is created first.")

        response = requests.patch(
            f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}/production-locations/{potential_match_os_id}/",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertEqual(response.status_code, HTTP_200_OK, f"Unexpected status code: {response.status_code}")
        expected_keys = {'os_id'}
        self.assertEqual(set(result.keys()), expected_keys, "Response JSON keys do not match expected keys.")

        approved_status = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}",
            headers=self.basic_headers,
        ).json()
        self.assertEqual(
            approved_status['status'],
            'APPROVED',
            "Moderation event status should be APPROVED after successful match"
        )

    def test_moderation_events_approval(self):
        # 1. Creates a new moderation event for the production location creation with the given details. ( POST /v1/production-locations/ )
        self.create_moderation_event()

        # 2. Create new production location from moderation event ( POST/v1/moderation-events/{moderation_id}/production-locations/ )
        response = requests.post(
            f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}/production-locations/",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertEqual(response.status_code, HTTP_201_CREATED, f"Unexpected status code: {response.status_code}")
        expected_keys = {'os_id'}
        self.assertEqual(set(result.keys()), expected_keys, "Response JSON keys do not match expected keys.")

    def test_moderation_events_rejection(self):
        # 1. Creates a new moderation event for the production location creation with the given details. ( POST /v1/production-locations/ )
        self.create_moderation_event()

        # 2. Change moderation event status to REJECTED ( PATCH /v1/moderation-events/{moderation_id}/ )
        status_rejected_payload = {
            'status': 'REJECTED'
        }
        response = requests.patch(
            f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}/",
            headers=self.basic_headers,
            json=status_rejected_payload,
        )
        result = response.json()
        self.assertEqual(response.status_code, HTTP_200_OK, f"Unexpected status code: {response.status_code}")
        self.assertEqual(result['status'], 'REJECTED', "Moderation event should have REJECTED status")

    def test_moderation_events_rate_limiting(self):
        self.create_moderation_event()
        for _ in range(500):
            response = requests.get(
                f"{self.root_url}/api/v1/moderation-events/{self.moderation_event_id}",
                headers=self.basic_headers,
            )
            if response.status_code == HTTP_429_TOO_MANY_REQUEST:
                self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUEST, "Expected 429 for rate-limited requests.")
                result = response.json()
                self.assertIn('Request was throttled', result['detail'], "Error message should be returned when rate-limited.")
                break
        else:
            self.skipTest("Rate limit was not reached; adjust loop count or rate-limit policy if needed.")
