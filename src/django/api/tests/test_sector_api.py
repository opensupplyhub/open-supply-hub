from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.urls import reverse


class SectorAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(SectorAPITest, self).setUp()
        self.url = reverse("facility-list")

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': ['Apparel', 'Agriculture']
    #     }), content_type='application/json')
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?sectors=Agriculture'
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)
