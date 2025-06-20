import json
from unittest.mock import Mock, patch

from api.models import ExtendedField
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.urls import reverse


class SectorTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    SECTOR_A = "Agriculture"
    SECTOR_B = "Apparel"
    SECTOR_NON_EXISTANT = "Encabulation"

    def setUp(self):
        super(SectorTest, self).setUp()
        self.url = reverse("facility-list")

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_array(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector_product_type': [self.SECTOR_A, self.SECTOR_B]
    #     }), content_type='application/json')
    #     response_data = json.loads(response.content)

    #     facility_index = FacilityIndex.objects.get(
    #         id=response_data['os_id'])
    #     self.assertIn(self.SECTOR_A, facility_index.sector)
    #     self.assertIn(self.SECTOR_B, facility_index.sector)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_string(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #    response = self.client.post(self.url, json.dumps({
    #        'country': "US",
    #        'name': "Azavea",
    #        'address': "990 Spring Garden St., Philadelphia PA 19123",
    #        'sector_product_type': '{}|{}'.format(
    #            self.SECTOR_A, self.SECTOR_B)
    #    }), content_type='application/json')
    #     response_data = json.loads(response.content)

    #     facility_index = FacilityIndex.objects.get(
    #         id=response_data['os_id'])
    #     self.assertIn(self.SECTOR_A, facility_index.sector)
    #     self.assertIn(self.SECTOR_B, facility_index.sector)

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
                    "sector_product_type": {},
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(0, ExtendedField.objects.all().count())
        self.assertEqual(response.status_code, 400)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_mixed_sector_product_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector_product_type': [
    #             self.SECTOR_A, self.SECTOR_B, self.SECTOR_NON_EXISTANT]
    #     }), content_type='application/json')
    #     response_data = json.loads(response.content)

    #     facility_index = FacilityIndex.objects.get(
    #         id=response_data['os_id'])
    #     self.assertIn(self.SECTOR_A, facility_index.sector)
    #     self.assertIn(self.SECTOR_B, facility_index.sector)

    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
    #     self.assertEqual({
    #         'raw_values': [self.SECTOR_NON_EXISTANT]
    #     }, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn(
    #         self.SECTOR_NON_EXISTANT.lower(), facility_index.product_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_product_types_only(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector_product_type': ['a', 'b']
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
    #     self.assertIn(Sector.DEFAULT_SECTOR_NAME, facility_index.sector)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_same_values_for_product_type_and_sector(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector_product_type':
    #         [self.SECTOR_A, self.SECTOR_B, self.SECTOR_NON_EXISTANT],
    #         'sector':
    #         [self.SECTOR_A, self.SECTOR_B, self.SECTOR_NON_EXISTANT],
    #         'product_type':
    #         [self.SECTOR_A, self.SECTOR_B, self.SECTOR_NON_EXISTANT],
    #     }), content_type='application/json')
    #     response_data = json.loads(response.content)

    #     item = FacilityListItem.objects.get(
    #         facility_id=response_data['os_id'])
    #     self.assertIn(self.SECTOR_A, item.sector)
    #     self.assertIn(self.SECTOR_B, item.sector)

    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
    #     self.assertEqual({
    #         'raw_values': [self.SECTOR_NON_EXISTANT]
    #     }, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn(
    #         self.SECTOR_NON_EXISTANT.lower(), facility_index.product_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_sector_product_type_contains_only_sector(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector_product_type':
    #         [self.SECTOR_A],
    #     }), content_type='application/json')
    #     response_data = json.loads(response.content)

    #     item = FacilityListItem.objects.get(
    #         facility_id=response_data['os_id'])
    #     self.assertIn(self.SECTOR_A, item.sector)
    #     self.assertEqual(0, ExtendedField.objects.all().count())
