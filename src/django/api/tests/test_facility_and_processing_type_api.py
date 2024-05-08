import json
from unittest.mock import Mock, patch

from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from api.processing import handle_external_match_process_result
from django.urls import reverse


class FacilityAndProcessingTypeAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(FacilityAndProcessingTypeAPITest, self).setUp()
        self.url = reverse("facility-list")

    def test_handle_match_process_result(self):
        result_obj_two = {
            'matches': [],
            'item_id': self.list_item_two.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_two.status,
        }

        result_two = handle_external_match_process_result(self.list_item_two.id, result_obj_two, None, True)
        self.assertEqual(result_two['status'], 'MATCHED')

        result_obj_three = {
            'matches': [],
            'item_id': self.list_item_three.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_three.status,
        }

        result_three = handle_external_match_process_result(self.list_item_three.id, result_obj_three, None, True)
        self.assertEqual(result_three['status'], 'POTENTIAL_MATCH')
        self.assertEqual(result_three['matches'][0]['confirm_match_url'], '/api/facility-matches/3/confirm/')
        self.assertEqual(result_three['matches'][0]['reject_match_url'], '/api/facility-matches/3/reject/')

        result_obj_four = {
            'matches': [],
            'item_id': self.list_item_four.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_four.status,
        }

        result_four = handle_external_match_process_result(self.list_item_four.id, result_obj_four, None, True)
        self.assertEqual(result_four['status'], 'NEW_FACILITY')

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_single_processing_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'processing_type': ['cutting']
    #     }), content_type='application/json')
    #     self.assertEqual(2, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.FACILITY_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'PROCESSING_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Cutting'
    #             ]
    #         ], 'raw_values': ['cutting']}, ef.value)
    #     ef = ExtendedField.objects.last()
    #     self.assertEqual(ExtendedField.PROCESSING_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'PROCESSING_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Cutting'
    #             ]
    #         ], 'raw_values': ['cutting']}, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertNotIn('Cutting', facility_index.facility_type)
    #     self.assertIn('Final Product Assembly', facility_index.facility_type)
    #     self.assertIn('Cutting', facility_index.processing_type)
    #     self.assertNotIn('Final Product Assembly',
    #                      facility_index.processing_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_multiple_facility_values(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'facility_type': ['office hq', 'final product assembly']
    #     }), content_type='application/json')
    #     self.assertEqual(2, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.FACILITY_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'FACILITY_TYPE',
    #                 'EXACT',
    #                 'Office / HQ',
    #                 'Office / HQ'
    #             ],
    #             [
    #                 'FACILITY_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Final Product Assembly'
    #             ]
    #         ], 'raw_values': ['office hq', 'final product assembly']},
    #         ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn('Final Product Assembly', facility_index.facility_type)
    #     self.assertIn('Office / HQ', facility_index.facility_type)
    #     self.assertEqual(0, len(facility_index.processing_type))

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_non_taxonomy_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'facility_type_processing_type': 'sewing|not a taxonomy value'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.filter(
    #         field_name='facility_type').count())
    #     self.assertEqual(1, ExtendedField.objects.filter(
    #         field_name='processing_type').count())
    #     self.assertEqual(response.status_code, 201)

    #     data = json.loads(response.content)
    #     index_row = FacilityIndex.objects.filter(id=data['os_id']).first()
    #     self.assertEqual(['Final Product Assembly'], index_row.facility_type)
    #     self.assertEqual(['Sewing'], index_row.processing_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_processing_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'processing_type': ['cutting']
    #     }), content_type='application/json')
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(self.url + '?processing_type=cutting')
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_facility_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': ['Health', 'Apparel'],
    #         'facility_type': ['office hq', 'final product assembly']
    #     }), content_type='application/json')
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?facility_type=final%20product%20assembly'
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    @patch("api.geocoding.requests.get")
    def test_search_by_facility_type_omits_nonapparel(self, mock_get):
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
                    "sector": "Health",
                    "facility_type": ["office hq", "final product assembly"],
                }
            ),
            content_type="application/json",
        )

        response = self.client.get(
            self.url + "?facility_type=final%20product%20assembly"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)
