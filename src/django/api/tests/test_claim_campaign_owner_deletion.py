from io import StringIO

from api.admin import ClaimCampaignAdmin
from api.models import ClaimCampaign, Contributor, User
from api.services.claim_campaign_service import resolve_claim_campaign
from api.tests.test_claim_campaign import ClaimCampaignBaseTest
from django.contrib.admin.sites import AdminSite
from django.core.management import call_command
from waffle.testutils import override_switch


class ClaimCampaignOwnerDeletionTest(ClaimCampaignBaseTest):
    """
    Deleting a brand that owns campaigns keeps the campaigns (closed and
    without an owner), so the claims attributed to them keep their
    campaign.
    """

    def setUp(self):
        super().setUp()
        self.claim = self.create_claim(
            campaign=self.campaign, via_link=True
        )
        # The claim's contributor (PROTECT) is the claimant, not the brand
        # being deleted.
        claimant = User.objects.create(email="claimant@example.com")
        self.claim.contributor = Contributor.objects.create(
            admin=claimant,
            name="claimant",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.claim.save()

    def delete_brand(self):
        call_command(
            "delete_user_and_contributor",
            email=self.user.email,
            stdout=StringIO(),
        )

    def test_command_deletes_a_brand_that_owns_campaigns(self):
        self.delete_brand()

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(
            Contributor.objects.filter(pk=self.contributor.pk).exists()
        )

    def test_campaign_is_kept_closed_and_ownerless(self):
        self.delete_brand()

        self.campaign.refresh_from_db()
        self.assertIsNone(self.campaign.contributor)
        self.assertEqual(ClaimCampaign.Status.CLOSED, self.campaign.status)

    def test_claims_keep_their_campaign(self):
        self.delete_brand()

        self.claim.refresh_from_db()
        self.assertEqual(self.campaign, self.claim.campaign)
        self.assertTrue(self.claim.via_link)

    def test_already_closed_campaign_stays_closed(self):
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()

        self.delete_brand()

        self.campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.CLOSED, self.campaign.status)

    def test_other_brands_campaigns_are_untouched(self):
        other_user = User.objects.create(email="other@example.com")
        other_campaign = ClaimCampaign.objects.create(
            contributor=Contributor.objects.create(
                admin=other_user,
                name="other brand",
                contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            ),
            name="Other campaign",
            code="OTHER-26",
        )

        self.delete_brand()

        other_campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.ACTIVE, other_campaign.status)
        self.assertIsNotNone(other_campaign.contributor)

    @override_switch("claim_campaigns", active=True)
    def test_ownerless_campaign_attributes_no_new_claims(self):
        self.delete_brand()

        self.assertEqual(
            (None, False),
            resolve_claim_campaign(self.facility, "EXAMPLE-FRESH-26"),
        )

    def test_admin_handles_an_ownerless_campaign(self):
        self.delete_brand()
        self.campaign.refresh_from_db()

        campaign_admin = ClaimCampaignAdmin(ClaimCampaign, AdminSite())
        self.assertFalse(campaign_admin.has_access(self.campaign))
