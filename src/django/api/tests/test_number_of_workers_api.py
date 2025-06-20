import json
from unittest.mock import Mock, patch

from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.urls import reverse


class NumberOfWorkersAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(NumberOfWorkersAPITest, self).setUp()
        self.url = reverse("facility-list")

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_single_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'number_of_workers': '2000'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.NUMBER_OF_WORKERS, ef.field_name)
    #     self.assertEqual({'min': 2000, 'max': 2000}, ef.value)

    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(1, len(facility_index.number_of_workers))
    #     self.assertIn('1001-5000', facility_index.number_of_workers)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_range_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'number_of_workers': '0-500'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.NUMBER_OF_WORKERS, ef.field_name)
    #     self.assertEqual({'min': 0, 'max': 500}, ef.value)

    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(1, len(facility_index.number_of_workers))
    #     self.assertIn('Less than 1000', facility_index.number_of_workers)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_crossrange_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'number_of_workers': '0 to 10000'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.NUMBER_OF_WORKERS, ef.field_name)
    #     self.assertEqual({'min': 0, 'max': 10000}, ef.value)

    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(3, len(facility_index.number_of_workers))
    #     self.assertIn('Less than 1000', facility_index.number_of_workers)
    #     self.assertIn('1001-5000', facility_index.number_of_workers)
    #     self.assertIn('5001-10000', facility_index.number_of_workers)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_maxrange_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'number_of_workers': '20,000-100,000'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.NUMBER_OF_WORKERS, ef.field_name)
    #     self.assertEqual({'min': 20000, 'max': 100000}, ef.value)

    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(1, len(facility_index.number_of_workers))
    #     self.assertIn('More than 10000', facility_index.number_of_workers)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_range(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'number_of_workers': '1500 to 2000'
    #     }), content_type='application/json')

    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?number_of_workers=1001-5000'
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    @patch("api.geocoding.requests.get")
    def test_search_without_matches(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.join_group_and_login()
        self.client.post(
            self.url,
            json.dumps(
                {
                    "country": "US",
                    "name": "Azavea",
                    "address": "990 Spring Garden St., Philadelphia PA 19123",
                    "sector": "Apparel",
                    "number_of_workers": "1000 to 9000",
                }
            ),
            content_type="application/json",
        )

        response = self.client.get(
            self.url + "?number_of_workers=More%20than%2010000"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)
