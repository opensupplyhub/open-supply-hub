import json
from unittest.mock import Mock, patch

from api.models import ExtendedField
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.urls import reverse


class ProductTypeTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(ProductTypeTest, self).setUp()
        self.url = reverse("facility-list")

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_array(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'product_type': ['a', 'b']
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
    #     self.assertEqual({
    #         'raw_values': ['a', 'b']
    #     }, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn('a', facility_index.product_type)
    #     self.assertIn('b', facility_index.product_type)
    #     self.assertIn('Apparel', facility_index.sector)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_string(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': "Apparel",
    #         'product_type': 'a|b'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
    #     self.assertEqual({
    #         'raw_values': ['a', 'b']
    #     }, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn('a', facility_index.product_type)
    #     self.assertIn('b', facility_index.product_type)
    #     self.assertIn('Apparel', facility_index.sector)

    @patch("api.geocoding.requests.get")
    def test_list_validation(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.join_group_and_login()
        response = self.client.post(
            self.url,
            json.dumps(
                {
                    "country": "US",
                    "name": "Azavea",
                    "address": "990 Spring Garden St., Philadelphia PA 19123",
                    "product_type": {},
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(0, ExtendedField.objects.all().count())
        self.assertEqual(response.status_code, 400)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_max_count(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': "Apparel",
    #         'product_type': [str(a) for a in range(MAX_PRODUCT_TYPE_COUNT)]
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(MAX_PRODUCT_TYPE_COUNT,
    #                      len(facility_index.product_type))

    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'product_type': [str(a)
    #                          for a in range(MAX_PRODUCT_TYPE_COUNT + 1)]
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     self.assertEqual(response.status_code, 400)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertEqual(MAX_PRODUCT_TYPE_COUNT,
    #                      len(facility_index.product_type))

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_product_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'product_type': ['a', 'b']
    #     }), content_type='application/json')

    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(self.url + '?product_type=A')
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)
