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
