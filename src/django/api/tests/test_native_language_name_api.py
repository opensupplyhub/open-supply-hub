from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase

from django.urls import reverse


class NativeLanguageNameAPITest(FacilityAPITestCaseBase):
    def setUp(self):
        super(NativeLanguageNameAPITest, self).setUp()
        self.url = reverse("facility-list")
        self.long_name = "杭州湾开发区兴慈二路与滨海二路叉口恒元工业园区A3"

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'sector': "Apparel",
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'native_language_name': self.long_name
    #     }), content_type='application/json')

    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?native_language_name={}'.format(self.long_name)
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)
