import unittest.mock
from rest_framework.test import APITestCase
from rest_framework import status


OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"


class TestProductionLocationsViewSet(APITestCase):

    def setUp(self):
        self.mock_search = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.os_id = "CN2021250D1DTN7"
        self.ohs_mock_response = {
            "count": 2,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                },
                {
                    "name": "location2",
                },
            ],
        }

    def test_get_production_locations(self):
        self.mock_search.return_value.search_index.return_value = self.ohs_mock_response
        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.data, self.ohs_mock_response)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location(self):
        self.mock_search.return_value.search_index.return_value = self.ohs_mock_response
        api_res = self.client.get(f"/api/v1/production-locations/{self.os_id}/")
        self.assertEqual(api_res.data, self.ohs_mock_response["data"][0])
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location_not_found(self):
        self.mock_search.return_value.search_index.return_value = {}
        api_res = self.client.get(f"/api/v1/production-locations/{self.os_id}/")
        self.assertEqual(api_res.data, {"message": "Production location not found!"})
        self.assertEqual(api_res.status_code, status.HTTP_404_NOT_FOUND)
