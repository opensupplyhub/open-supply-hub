import json
from api.constants import FacilityClaimStatuses
from api.models import FacilityClaim
from api.models.facility.facility_index import FacilityIndex
from api.extended_fields import create_extendedfields_for_claim
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from waffle.testutils import override_switch

from django.urls import reverse


class IndexFacilitiesTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(IndexFacilitiesTest, self).setUp()
        self.url = reverse("facility-list")

    def test_facility_index_contains_sector(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(["Apparel"], facility_index.sector)

    def test_sector_reamins_in_index_if_match_is_deactivated(self):
        self.match.is_active = False
        self.match.save()
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(["Apparel"], facility_index.sector)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_posting_to_new_facility_should_create_index_with_sector(
    #         self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     resp = self.client.post(self.url, {
    #         'sector': "Mining",
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #     })
    #     mock_get.assert_called()
    #     self.assertEqual(resp.status_code, 201)
    #     self.assertEqual(len(resp.data['matches']), 0)
    #     facility_id = resp.data['os_id']
    #     facility_index = FacilityIndex.objects.get(id=facility_id)
    #     self.assertIn('Mining', facility_index.sector)
    #     self.assertNotIn('Apparel', facility_index.sector)
    #     self.assertEqual(len(facility_index.sector), 1)

    # @patch('api.geocoding.requests.get')
    # def test_posting_to_existing_facility_should_update_sector(
    #         self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     resp = self.client.post(self.url, {
    #         'sector': ["Mining", "Mechanical Engineering"],
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #     })
    #     self.assertEqual(resp.status_code, 201)
    #     self.assertEqual(len(resp.data['matches']), 0)
    #     facility_id = resp.data['os_id']

    #     resp = self.client.post(self.url, {
    #         'sector': ["Mining", "Metal Manufacturing"],
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #     })
    #     self.assertEqual(resp.status_code, 201)
    #     self.assertEqual(resp.data['os_id'], facility_id)
    #     facility_index = FacilityIndex.objects.get(id=facility_id)
    #     self.assertIn('Mining', facility_index.sector)
    #     self.assertIn('Metal Manufacturing', facility_index.sector)
    #     self.assertNotIn('Apparel', facility_index.sector)
    #     self.assertEqual(len(facility_index.sector), 2)

    @override_switch("claim_a_facility", active=True)
    def test_updating_claim_sector_and_production_types_updates_index(self):
        facility_production_types_mocked = [
            'advanced battery industry',
            'batteries',
            'energy storage',
            'minerals',
            'renewables'
        ]

        claim_data = dict(
            contact_person="Name",
            facility_phone_number='12345',
            company_name="Test",
            website="http://example.com",
            facility_description="description",
            facility_production_types=facility_production_types_mocked,
        )
        facility_claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            status=FacilityClaimStatuses.APPROVED,
            **claim_data,
        )
        create_extendedfields_for_claim(facility_claim)
        self.join_group_and_login()
        response = self.client.put(
            "/api/facility-claims/{}/claimed/".format(facility_claim.id),
            json.dumps(
                {
                    **claim_data,
                    "sector": ["Mining"],
                    "facility_phone_number_publicly_visible": False,
                    "point_of_contact_publicly_visible": False,
                    "office_info_publicly_visible": False,
                    "facility_website_publicly_visible": False,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(200, response.status_code)

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Mining", facility_index.sector)
        facility_production_types_processed = (
            facility_index.approved_claim["facility_production_types"]
        )
        self.assertListEqual(
            facility_production_types_mocked,
            facility_production_types_processed
        )
