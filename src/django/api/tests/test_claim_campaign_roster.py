from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimCampaign,
    ClaimCampaignSupplier,
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.services.claim_campaign_service import (
    generate_campaign_code,
    resolve_claim_campaign,
)
from api.tests.test_claim_campaign import ClaimCampaignBaseTest
from waffle.testutils import override_flag, override_switch

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

SELF_SERVE = "claim_campaign_self_serve"


class ClaimCampaignRosterBaseTest(ClaimCampaignBaseTest):
    """Adds a second facility on the same list and logs the brand in."""

    def setUp(self):
        super().setUp()

        self.password = "example123"
        self.user.set_password(self.password)
        self.user.save()

        self.list_item.facility = self.facility
        self.list_item.save()

        self.other_item = FacilityListItem.objects.create(
            name="Other",
            address="Other address",
            country_code="BD",
            sector=["Apparel"],
            row_index=2,
            geocoded_point=Point(1, 1),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.other_facility = Facility.objects.create(
            name="Other",
            address="Other address",
            country_code="BD",
            location=Point(1, 1),
            created_from=self.other_item,
        )
        self.other_item.facility = self.other_facility
        self.other_item.save()

        self.client.login(email=self.user.email, password=self.password)

    def add_to_roster(self, campaign, *facilities):
        for facility in facilities:
            ClaimCampaignSupplier.objects.create(
                campaign=campaign, facility=facility
            )


class ClaimCampaignCodeTest(ClaimCampaignBaseTest):
    def test_code_is_saved_upper_case(self):
        campaign = ClaimCampaign.objects.create(
            contributor=self.contributor, name="Lower", code=" lower-26 "
        )
        self.assertEqual("LOWER-26", campaign.code)

    def test_code_rejects_characters_unsafe_for_links(self):
        campaign = ClaimCampaign(
            contributor=self.contributor, name="Bad", code="BAD CODE/26"
        )
        with self.assertRaises(ValidationError):
            campaign.full_clean()

    def test_generated_code_uses_contributor_name(self):
        code = generate_campaign_code("Meridian Apparel Co.")
        self.assertRegex(code, r"^MERIDIAN-[A-Z2-9]{6}$")


@override_switch("claim_campaigns", active=True)
class ClaimCampaignRosterAttributionTest(ClaimCampaignRosterBaseTest):
    def test_lower_case_link_code_is_attributed(self):
        self.assertEqual(
            (self.campaign, True),
            resolve_claim_campaign(self.facility, "example-fresh-26"),
        )

    def test_claim_is_attributed_to_the_campaign_whose_roster_has_it(self):
        food = ClaimCampaign.objects.create(
            contributor=self.contributor, name="Food", code="FOOD-26"
        )
        non_food = ClaimCampaign.objects.create(
            contributor=self.contributor, name="Non-food", code="NONFOOD-26"
        )
        self.add_to_roster(food, self.facility)
        self.add_to_roster(non_food, self.other_facility)
        # The original list-based campaign is closed once the brand
        # moves to chosen rosters.
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()

        self.assertEqual(
            (food, False), resolve_claim_campaign(self.facility, None)
        )
        self.assertEqual(
            (non_food, False),
            resolve_claim_campaign(self.other_facility, None),
        )

    def test_facility_left_off_a_roster_is_not_attributed_to_it(self):
        self.add_to_roster(self.campaign, self.other_facility)
        self.assertEqual(
            (None, False), resolve_claim_campaign(self.facility, None)
        )


@override_switch("claim_campaigns", active=True)
class ClaimCampaignRosterDashboardTest(ClaimCampaignRosterBaseTest):
    url = "/api/claim-campaigns/"

    def test_campaign_without_roster_lists_every_list_facility(self):
        [campaign] = self.client.get(self.url).json()
        self.assertEqual(
            {self.facility.id, self.other_facility.id},
            {s["os_id"] for s in campaign["suppliers"]},
        )

    def test_campaign_with_roster_lists_only_chosen_suppliers(self):
        self.add_to_roster(self.campaign, self.other_facility)
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.other_facility,
            contact_person="Name",
            company_name="Test",
            facility_description="description",
            status=FacilityClaimStatuses.PENDING,
        )

        [campaign] = self.client.get(self.url).json()
        self.assertEqual(
            [
                {
                    "os_id": self.other_facility.id,
                    "name": "Other",
                    "country_code": "BD",
                    "claim_status": "pending",
                    "is_closed": False,
                    "last_invite": None,
                }
            ],
            campaign["suppliers"],
        )


@override_switch("claim_campaigns", active=True)
class ClaimCampaignSelfServeTest(ClaimCampaignRosterBaseTest):
    url = "/api/claim-campaigns/"
    candidates_url = "/api/claim-campaigns/candidates/"

    def create_payload(self, **overrides):
        return {
            "name": "Meridian onboarding",
            "list_id": self.facility_list.id,
            "os_ids": [self.facility.id],
            **overrides,
        }

    @override_flag(SELF_SERVE, active=False)
    def test_candidates_and_create_are_hidden_without_the_flag(self):
        self.assertEqual(404, self.client.get(self.candidates_url).status_code)
        response = self.client.post(
            self.url, self.create_payload(), format="json"
        )
        self.assertEqual(404, response.status_code)

    @override_flag(SELF_SERVE, active=True)
    @override_switch("claim_campaigns", active=False)
    def test_everything_is_hidden_when_the_switch_is_off(self):
        self.assertEqual(404, self.client.get(self.candidates_url).status_code)

    @override_flag(SELF_SERVE, active=True)
    def test_candidates_lists_own_active_lists_including_private(self):
        private_list = FacilityList.objects.create(
            header="header", file_name="two", name="Research"
        )
        Source.objects.create(
            facility_list=private_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=False,
            contributor=self.contributor,
        )

        lists = self.client.get(self.candidates_url).json()
        self.assertEqual(
            {("List", True), ("Research", False)},
            {(entry["name"], entry["is_public"]) for entry in lists},
        )

    @override_flag(SELF_SERVE, active=True)
    def test_candidates_for_a_list_returns_suppliers_with_status(self):
        response = self.client.get(
            self.candidates_url, {"list": self.facility_list.id}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [self.facility.id, self.other_facility.id],
            [s["os_id"] for s in response.json()["suppliers"]],
        )
        self.assertEqual(
            {"unclaimed"},
            {s["claim_status"] for s in response.json()["suppliers"]},
        )

    @override_flag(SELF_SERVE, active=True)
    def test_candidates_for_another_contributors_list_is_not_found(self):
        stranger = Contributor.objects.create(
            admin=User.objects.create(email="other@example.com"),
            name="Other brand",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        their_list = FacilityList.objects.create(
            header="header", file_name="three", name="Theirs"
        )
        Source.objects.create(
            facility_list=their_list,
            source_type=Source.LIST,
            contributor=stranger,
        )
        response = self.client.get(
            self.candidates_url, {"list": their_list.id}
        )
        self.assertEqual(404, response.status_code)

    @override_flag(SELF_SERVE, active=True)
    def test_create_makes_an_active_campaign_with_the_chosen_roster(self):
        response = self.client.post(
            self.url, self.create_payload(), format="json"
        )
        self.assertEqual(201, response.status_code)

        body = response.json()
        self.assertEqual("Meridian onboarding", body["name"])
        self.assertEqual("ACTIVE", body["status"])
        self.assertRegex(body["code"], r"^TEST-[A-Z2-9]{6}$")
        self.assertEqual(
            [self.facility.id], [s["os_id"] for s in body["suppliers"]]
        )

        campaign = ClaimCampaign.objects.get(code=body["code"])
        self.assertEqual(self.contributor, campaign.contributor)
        self.assertEqual(
            [self.facility.id],
            list(campaign.suppliers.values_list("facility_id", flat=True)),
        )

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_os_ids_that_are_not_on_the_list(self):
        response = self.client.post(
            self.url,
            self.create_payload(os_ids=[self.facility.id, "US2026XXXXXXX"]),
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("US2026XXXXXXX", str(response.json()["os_ids"]))
        self.assertEqual(1, ClaimCampaign.objects.count())

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_an_inactive_list(self):
        self.source.is_active = False
        self.source.save()
        response = self.client.post(
            self.url, self.create_payload(), format="json"
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("list_id", response.json())


@override_switch("claim_campaigns", active=True)
class ClaimCampaignCreateValidationTest(ClaimCampaignRosterBaseTest):
    url = "/api/claim-campaigns/"

    def post(self, **overrides):
        return self.client.post(
            self.url,
            {
                "name": "Meridian onboarding",
                "list_id": self.facility_list.id,
                "os_ids": [self.facility.id, self.other_facility.id],
                **overrides,
            },
            format="json",
        )

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_an_already_claimed_supplier(self):
        self.create_claim(status=FacilityClaimStatuses.APPROVED)
        response = self.post()
        self.assertEqual(400, response.status_code)
        self.assertIn(self.facility.id, str(response.json()["os_ids"]))
        self.assertEqual(1, ClaimCampaign.objects.count())

    @override_flag(SELF_SERVE, active=True)
    def test_create_allows_a_supplier_with_a_pending_claim(self):
        self.create_claim(status=FacilityClaimStatuses.PENDING)
        self.assertEqual(201, self.post().status_code)

    @override_flag(SELF_SERVE, active=True)
    def test_create_allows_a_supplier_whose_claim_was_revoked(self):
        self.create_claim(status=FacilityClaimStatuses.REVOKED)
        self.assertEqual(201, self.post().status_code)

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_a_whitespace_only_name(self):
        response = self.post(name="   \n\t ")
        self.assertEqual(400, response.status_code)
        self.assertIn("name", response.json())

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_a_name_over_100_characters(self):
        self.assertEqual(400, self.post(name="x" * 101).status_code)
        self.assertEqual(201, self.post(name="x" * 100).status_code)

    @override_flag(SELF_SERVE, active=True)
    def test_create_tidies_whitespace_and_keeps_unicode(self):
        response = self.post(name="  Café\n onboarding   2026 🌱 <b>x</b> ")
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            "Café onboarding 2026 🌱 <b>x</b>", response.json()["name"]
        )

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_a_duplicate_name_ignoring_case(self):
        response = self.post(name="  fresh produce SUPPLIERS 2026 ")
        self.assertEqual(400, response.status_code)
        self.assertIn("name", response.json())

    @override_flag(SELF_SERVE, active=True)
    def test_create_rejects_a_closed_supplier_from_a_list(self):
        self.other_facility.is_closed = True
        self.other_facility.save()
        response = self.post()
        self.assertEqual(400, response.status_code)
        self.assertIn("Closed", str(response.json()["os_ids"]))
