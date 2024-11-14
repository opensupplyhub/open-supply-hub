import unittest.mock
from rest_framework.test import APITestCase
from rest_framework import status

OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"

class TestProductionLocationsViewSet(APITestCase):

    def test_get_production_locations(self):
        mock_res = {
            'count': 0,
            'data': [
                {'name': 'location1'},
                {'name': 'location2'}
            ]
        }

        with unittest.mock.patch(OPEN_SEARCH_SERVICE) as mock_search:
            mock_search.return_value.search_index.return_value = mock_res
            api_res = self.client.get('/api/v1/production-locations/')
            self.assertEqual(api_res.data, mock_res)
            self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location(self):
        os_id = 'CN2021250D1DTN7'
        mock_res = {
            'count': 1,
            'data': [
                {
                    'os_id': os_id,
                    'name': 'location1'
                }
            ]
        }

        with unittest.mock.patch(OPEN_SEARCH_SERVICE) as mock_search:
            mock_search.return_value.search_index.return_value = mock_res
            api_res = self.client.get(f'/api/v1/production-locations/{os_id}/')
            self.assertEqual(api_res.data, mock_res['data'][0])
            self.assertEqual(api_res.status_code, status.HTTP_200_OK)
