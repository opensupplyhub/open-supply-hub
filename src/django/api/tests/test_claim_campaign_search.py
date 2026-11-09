from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimCampaign,
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.tests.test_claim_campaign_roster import ClaimCampaignRosterBaseTest
from waffle.testutils import override_flag, override_switch

from django.contrib.gis.geos import Point

SELF_SERVE = "claim_campaign_self_serve"


@override_switch("claim_campaigns", active=True)
@override_flag(SELF_SERVE, active=True)
class ClaimCampaignSearchTest(ClaimCampaignRosterBaseTest):
    """
    Choosing campaign suppliers from a search of OS Hub, including
    facilities the brand didn't contribute.
    """

    url = "/api/claim-campaigns/"
    search_url = "/api/claim-campaigns/candidates/search/"

    def setUp(self):
        super().setUp()
        other_user = User.objects.create(email="other@example.com")
        other_brand = Contributor.objects.create(
            admin=other_user,
            name="Other Brand",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        other_list = FacilityList.objects.create(
            header="header", file_name="other", name="Other list"
        )
        other_source = Source.objects.create(
            facility_list=other_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=other_brand,
        )
        self.not_mine = self.make_facility(
            other_source, "Lotus Knitwear", "VN", row_index=1
        )
        self.closed = self.make_facility(
            other_source, "Lotus Closed Mill", "VN", row_index=2
        )
        self.closed.is_closed = True
        self.closed.save()

    def make_facility(self, source, name, country, row_index):
        item = FacilityListItem.objects.create(
            name=name,
            address=f"{name} address",
            country_code=country,
            sector=["Apparel"],
            row_index=row_index,
            geocoded_point=Point(2, 2),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility = Facility.objects.create(
            name=name,
            address=f"{name} address",
            country_code=country,
            location=Point(2, 2),
            created_from=item,
        )
        item.facility = facility
        item.save()
        return facility

    def search(self, query):
        return self.client.get(f"{self.search_url}?{query}")

    def test_search_finds_facilities_the_brand_did_not_contribute(self):
        response = self.search("countries=VN")

        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(1, data["count"])
        self.assertEqual(
            [
                {
                    "os_id": self.not_mine.id,
                    "name": "Lotus Knitwear",
                    "country_code": "VN",
                    "claim_status": "unclaimed",
                }
            ],
            data["suppliers"],
        )

    def test_search_leaves_out_closed_facilities(self):
        os_ids = [s["os_id"] for s in self.search("q=Lotus").json()["suppliers"]]
        self.assertNotIn(self.closed.id, os_ids)

    def test_search_needs_at_least_one_filter(self):
        response = self.search("sort_by=name_asc")
        self.assertEqual(400, response.status_code)

    @override_flag(SELF_SERVE, active=False)
    def test_search_is_hidden_without_the_flag(self):
        self.assertEqual(404, self.search("countries=VN").status_code)

    def test_create_from_search_with_facilities_not_on_my_lists(self):
        response = self.client.post(
            self.url,
            {"name": "Vietnam outreach", "os_ids": [self.not_mine.id]},
            format="json",
        )

        self.assertEqual(201, response.status_code)
        campaign = ClaimCampaign.objects.get(name="Vietnam outreach")
        self.assertEqual(
            [self.not_mine.id],
            [s.facility_id for s in campaign.suppliers.all()],
        )

    def test_create_from_search_refuses_closed_facilities(self):
        response = self.client.post(
            self.url,
            {"name": "Closed", "os_ids": [self.not_mine.id, self.closed.id]},
            format="json",
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("Closed", str(response.json()))
        self.assertFalse(ClaimCampaign.objects.filter(name="Closed").exists())

    def test_create_from_search_refuses_claimed_facilities(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.not_mine,
            contact_person="Name",
            company_name="Test",
            facility_description="description",
            status=FacilityClaimStatuses.APPROVED,
        )
        response = self.client.post(
            self.url,
            {"name": "Claimed", "os_ids": [self.not_mine.id]},
            format="json",
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("already claimed", str(response.json()))

    def test_create_from_search_refuses_unknown_os_ids(self):
        response = self.client.post(
            self.url,
            {"name": "Unknown", "os_ids": ["VN0000000000000"]},
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("not found", str(response.json()))
