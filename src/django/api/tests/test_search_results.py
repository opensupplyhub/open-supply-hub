
import unittest.mock
from rest_framework.test import APITestCase
from rest_framework import status
OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"


class SearchResultsTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.name = 'CHANG+KNITTING+FACTORY'
        self.address = 'TONGHU+ECONOMIC+DEVELOPMENT+ZONE，HUIZHOU%2C+CHINA'
        self.county_alpha_2_code = 'CN'
        self.name1 = 'test name'
        self.address1 = 'test address'
        self.county_alpha_2_code1 = 'AX'

        self.search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.search_index_mock = self.search_mock.return_value.search_index
        self.search_results_response_mock = {
            "count": 2,
            "data": [
              {
                "sector": [
                    "Apparel"
                ],
                "coordinates": {
                    "lat": 23.082231,
                    "lng": 114.196658
                },
                "os_id": "CN2025016GP2VEJ",
                "country": {
                    "alpha_2": "CN",
                    "alpha_3": "CHN",
                    "name": "China",
                    "numeric": "156"
                },
                "claim_status": "unclaimed",
                "address": "KIU HING ROAD, 2-12 TONGHU, CHINA",
                "name": "XIN CHANG CHANG KNITTING FACTORY"
                },
              {
                "sector": [
                    "Apparel"
                ],
                "coordinates": {
                    "lat": 30.607581,
                    "lng": 120.55107
                },
                "os_id": "CN2025016RHMQVG",
                "country": {
                    "alpha_2": "CN",
                    "alpha_3": "CHN",
                    "name": "China",
                    "numeric": "156"
                },
                "claim_status": "unclaimed",
                "address": "No. 2 Industrial Area Economic, Zhejiang Province",
                "name": "Tongxiang Miracle Knitting Factory Co. Ltd."
              }
            ],
        }

    def get_url(self, name, address, county_code):
        return (f"/api/v1/production-locations/?name={name}&address={address}"
                "&country={county_code}")

    def test_receive_search_results_data(self):
        self.search_index_mock.return_value = self.search_results_response_mock
        api_res = self.client.get(
            self.get_url(self.name, self.address, self.county_alpha_2_code))
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertEqual(api_res.data, self.search_results_response_mock)
        self.assertEqual(len(api_res.data.get("data")),
                         api_res.data.get("count"))

    def test_get_search_results_not_found(self):
        self.search_index_mock.return_value = {"data": [], "count": 0}
        api_res = self.client.get(
            self.get_url(self.name1, self.address1, self.county_alpha_2_code1))
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(api_res.data.get("data")), 0)
        self.assertEqual(api_res.data.get("count"), 0)
