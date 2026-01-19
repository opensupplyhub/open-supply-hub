import unittest.mock
from rest_framework.test import APITestCase
from rest_framework import status
from api.views.v1.response_mappings.production_locations_response \
    import ProductionLocationsResponseMapping


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

    def test_get_production_locations_includes_geocode_fields(self):
        response_with_geocode = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                    "geocoded_location_type": "ROOFTOP",
                    "geocoded_address": "123 Main St, City, Country",
                }
            ],
        }
        self.search_index_mock.return_value = response_with_geocode
        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertIn("data", api_res.data)
        self.assertEqual(len(api_res.data["data"]), 1)
        item = api_res.data["data"][0]
        self.assertEqual(item.get("geocoded_location_type"), "ROOFTOP")
        self.assertEqual(
            item.get("geocoded_address"), "123 Main St, City, Country"
        )

    def test_get_single_production_location_includes_geocode_fields(self):
        response_with_geocode = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                    "geocoded_location_type": "RANGE_INTERPOLATED",
                    "geocoded_address": "456 Side Rd, Town, Country",
                }
            ],
        }
        self.search_index_mock.return_value = response_with_geocode
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            api_res.data.get("geocoded_location_type"), "RANGE_INTERPOLATED"
        )
        self.assertEqual(
            api_res.data.get("geocoded_address"), "456 Side Rd, Town, Country"
        )

    def test_production_locations_response_mapping(self):
        self.search_index_mock.return_value = {"count": 0, "data": []}

        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

        args = self.search_index_mock.call_args[0]
        self.assertEqual(len(args), 2)
        query_body = args[1]
        self.assertIn("_source", query_body)
        self.assertListEqual(
            query_body["_source"],
            ProductionLocationsResponseMapping.PRODUCTION_LOCATIONS,
        )

    def test_single_production_location_response_mapping(self):
        self.search_index_mock.return_value = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                }
            ],
        }

        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

        args = self.search_index_mock.call_args[0]
        self.assertEqual(len(args), 2)
        query_body = args[1]
        self.assertIn("_source", query_body)
        self.assertListEqual(
            query_body["_source"],
            ProductionLocationsResponseMapping.PRODUCTION_LOCATION_BY_OS_ID,
        )
