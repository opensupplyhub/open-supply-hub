import json

from rest_framework.test import APITestCase
from django.urls import reverse


class TestPageLimitInFacilitiesViewsetListAction(APITestCase):
    def setUp(self):
        self.url = reverse('facility-list')

    def test_page_limit_blocks_request_when_exceeding_limit(self):
        expected_response = {
            'page': [
                ('This value must be less or equal to 100. If you need access '
                 'to more data, please contact support@opensupplyhub.org.')
            ]
        }

        page = {'page': 101}

        response = self.client.get(self.url, page)
        self.assertEqual(response.status_code, 400)

        response_body_dict = json.loads(response.content)
        self.assertEqual(response_body_dict, expected_response)

    def test_page_limit_does_not_block_request_within_limit(self):
        page = {'page': 1}

        response = self.client.get(self.url, page)
        response_body_dict = json.loads(response.content)

        # Made sure that the successful response with an empty facility list
        # is returned even if the test database is empty.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body_dict['count'], 0)
