import unittest.mock
from rest_framework.test import APITestCase
from rest_framework import status


OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"


class TestProductionLocationsViewSet(APITestCase):

    def setUp(self):
        self.search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.search_index_mock = self.search_mock.return_value.search_index
        self.os_id = "CN2021250D1DTN7"
        self.ohs_response_mock = {
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
        self.search_index_mock.return_value = self.ohs_response_mock
        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.data, self.ohs_response_mock)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location(self):
        self.search_index_mock.return_value = self.ohs_response_mock
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.data, self.ohs_response_mock["data"][0])
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location_not_found(self):
        self.search_index_mock.return_value = {}
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        detail = {"detail": "The location with the given id was not found."}
        self.assertEqual(api_res.data, detail)
        self.assertEqual(api_res.status_code, status.HTTP_404_NOT_FOUND)
