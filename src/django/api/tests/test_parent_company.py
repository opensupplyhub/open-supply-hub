from unittest import skip
from unittest.mock import Mock, patch

from api.models import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.urls import reverse


class ParentCompanyTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(ParentCompanyTest, self).setUp()
        self.url = reverse("facility-list")

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_submit_parent_company_no_match(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'parent_company': 'A random value'
    #     })
    #     self.assertEqual(1, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.PARENT_COMPANY, ef.field_name)
    #     self.assertEqual({
    #         'raw_value': 'A random value',
    #         'name': 'A random value'
    #     }, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn('A random value', facility_index.parent_company_name)
    #     self.assertEqual(0, len(facility_index.parent_company_id))

    @skip("Skip fuzzy matching. Will revisit at #1805")
    @patch("api.geocoding.requests.get")
    def test_submit_parent_company_fuzzy_match(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.join_group_and_login()
        self.client.post(
            self.url,
            {
                "country": "US",
                "name": "Azavea",
                "address": "990 Spring Garden St., Philadelphia PA 19123",
                "parent_company": "TEST CONTRIBUTOR",
            },
        )
        self.assertEqual(1, ExtendedField.objects.all().count())
        ef = ExtendedField.objects.first()
        self.assertEqual(ExtendedField.PARENT_COMPANY, ef.field_name)
        self.assertEqual(
            {
                "raw_value": "TEST CONTRIBUTOR",
                "contributor_name": self.contributor.name,
                "contributor_id": self.contributor.id,
            },
            ef.value,
        )
        facility_index = FacilityIndex.objects.get(id=ef.facility.id)
        self.assertIn(
            self.contributor.name, facility_index.parent_company_name
        )
        self.assertIn(self.contributor.id, facility_index.parent_company_id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_submit_parent_company_duplicate(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': "Apparel",
    #         'parent_company': 'test contributor 1'
    #     })
    #     self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': "Apparel",
    #         'parent_company': 'test contributor 1'
    #     })
    #     self.assertEqual(2, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn(self.contributor.name,
    #                   facility_index.parent_company_name)
    #     self.assertEqual(1, len(facility_index.parent_company_name))
    #     self.assertIn(self.contributor.id, facility_index.parent_company_id)
    #     self.assertEqual(1, len(facility_index.parent_company_id))

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_name(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'parent_company': 'test contributor 1'
    #     })
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?parent_company={}'.format(self.contributor.id)
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_id(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'parent_company': 'test contributor 1'
    #     })
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?parent_company={}'.format(self.contributor.name)
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_multiple(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, {
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'parent_company': 'test contributor 1'
    #     })
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?parent_company={}?parent_company={}'.format(
    #             self.contributor.name, self.contributor.id
    #         )
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)
