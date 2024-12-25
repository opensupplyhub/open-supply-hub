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

    def test_create_moderation_event(self):
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
        print(f'[Contribution Record; moderation id:] {self.moderation_event_id}')

