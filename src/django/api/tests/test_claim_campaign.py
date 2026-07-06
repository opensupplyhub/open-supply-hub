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
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError


class ClaimCampaignBaseTest(APITestCase):
    """
    Shared fixtures for the claim campaign test suites. Holds no tests
    of its own so subclasses do not re-run inherited ones.
    """

    def setUp(self):
        self.user = User.objects.create(email="test@example.com")

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility_list = FacilityList.objects.create(
            header="header", file_name="one", name="List"
        )

        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.campaign = ClaimCampaign.objects.create(
            contributor=self.contributor,
            name="Fresh Produce Suppliers 2026",
            code="EXAMPLE-FRESH-26",
        )

    def create_claim(self, **kwargs):
        return FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="Name",
            company_name="Test",
            facility_description="description",
            **kwargs,
        )


class ClaimCampaignTest(ClaimCampaignBaseTest):
    def test_campaign_is_created_with_defaults(self):
        self.assertIsNotNone(self.campaign.uuid)
        self.assertEqual(ClaimCampaign.Status.ACTIVE, self.campaign.status)
        self.assertEqual(
            "Fresh Produce Suppliers 2026 (EXAMPLE-FRESH-26)",
            str(self.campaign),
        )

    def test_duplicate_campaign_code_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClaimCampaign.objects.create(
                    contributor=self.contributor,
                    name="Another campaign",
                    code="EXAMPLE-FRESH-26",
                )

    def test_claim_defaults_have_no_campaign(self):
        claim = self.create_claim()
        self.assertIsNone(claim.campaign)
        self.assertFalse(claim.via_link)

    def test_claim_can_be_attributed_to_campaign(self):
        claim = self.create_claim(campaign=self.campaign, via_link=True)
        claim.refresh_from_db()
        self.assertEqual(self.campaign, claim.campaign)
        self.assertTrue(claim.via_link)

    def test_campaign_with_claims_cannot_be_deleted(self):
        self.create_claim(campaign=self.campaign)
        with self.assertRaises(ProtectedError):
            self.campaign.delete()


@override_switch("claim_campaigns", active=True)
class ClaimCampaignAttributionTest(ClaimCampaignBaseTest):
    def setUp(self):
        super().setUp()

        self.password = "example123"
        self.user.set_password(self.password)
        self.user.save()

        # Matched list items carry the facility reference; the roster
        # lookup relies on it.
        self.list_item.facility = self.facility
        self.list_item.save()

        self.claim_url = f"/api/facilities/{self.facility.id}/claim/"
        self.claim_data = {
            "your_name": "John Doe",
            "your_title": "Facility Manager",
            "your_business_website": "https://example.com",
            "business_website": "https://facility.com",
            "business_linkedin_profile": "",
            "facility_description": "description",
        }

        self.client.login(email=self.user.email, password=self.password)

    def post_claim(self, **extra):
        response = self.client.post(
            self.claim_url, {**self.claim_data, **extra}
        )
        self.assertEqual(200, response.status_code)
        return FacilityClaim.objects.get(facility=self.facility)

    @override_switch("claim_a_facility", active=True)
    def test_claim_with_valid_code_is_attributed_via_link(self):
        claim = self.post_claim(campaign="EXAMPLE-FRESH-26")
        self.assertEqual(self.campaign, claim.campaign)
        self.assertTrue(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_claim_without_code_is_attributed_from_single_roster(self):
        claim = self.post_claim()
        self.assertEqual(self.campaign, claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_claim_without_code_and_ambiguous_rosters_is_not_attributed(
        self,
    ):
        other_user = User.objects.create(email="other@example.com")
        other_contributor = Contributor.objects.create(
            admin=other_user,
            name="other contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        other_list = FacilityList.objects.create(
            header="header", file_name="two", name="Other list"
        )
        other_source = Source.objects.create(
            facility_list=other_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=other_contributor,
        )
        FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=other_source,
            facility=self.facility,
        )
        ClaimCampaign.objects.create(
            contributor=other_contributor,
            name="Other campaign",
            code="OTHER-26",
        )

        claim = self.post_claim()
        self.assertIsNone(claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_claim_with_unusable_code_is_created_without_campaign(self):
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()

        claim = self.post_claim(campaign="UNKNOWN-CODE")
        self.assertIsNone(claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_claim_from_replaced_list_is_not_attributed(self):
        self.source.is_active = False
        self.source.save()

        claim = self.post_claim()
        self.assertIsNone(claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_unknown_code_falls_back_to_roster_attribution(self):
        claim = self.post_claim(campaign="TYPO-CODE")
        self.assertEqual(self.campaign, claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    @override_switch("claim_campaigns", active=False)
    def test_no_attribution_while_switch_is_off(self):
        claim = self.post_claim(campaign="EXAMPLE-FRESH-26")
        self.assertIsNone(claim.campaign)
        self.assertFalse(claim.via_link)
