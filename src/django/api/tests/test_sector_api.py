import json

from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase

from django.urls import reverse


class SectorAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(SectorAPITest, self).setUp()
        self.url = reverse("facility-list")

    def test_search(self):
        self.join_group_and_login()

        response = self.client.get(
            self.url + '?detail=true'
        )
        data = json.loads(response.content)

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['features'][0]['id'], self.facility.id)
        self.assertEqual(len(data['features'][0]['properties']['sector']), 1)
        self.assertEqual(data['features'][0]['properties']
                         ['sector'][0]['values'],
                         ['Apparel'])

    def test_search_without_detail(self):
        self.join_group_and_login()

        response = self.client.get(
            self.url
        )
        data = json.loads(response.content)

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['features'][0]['id'], self.facility.id)
        self.assertNotIn('sector', data['features'][0]['properties'])
