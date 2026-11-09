from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimCampaign,
    ClaimCampaignSupplier,
    Facility,
    FacilityClaimInvite,
    FacilityListItem,
    FacilityMatch,
    User,
)
from api.services.claim_campaign_service import (
    get_claim_statuses,
    move_campaign_suppliers,
)
from api.signals import location_post_delete_handler_for_opensearch
from api.tests.test_claim_campaign_roster import ClaimCampaignRosterBaseTest
from waffle.testutils import override_flag, override_switch

from django.db.models.signals import post_delete

SELF_SERVE = "claim_campaign_self_serve"


class ClaimStatusEdgeCaseTest(ClaimCampaignRosterBaseTest):
    """How each mix of claims on a facility reads on the dashboard."""

    def status(self):
        return get_claim_statuses([self.facility.id])[self.facility.id]

    def test_no_claims_reads_as_not_started(self):
        self.assertEqual("unclaimed", self.status())

    def test_denied_claim_reads_as_not_started(self):
        self.create_claim(status=FacilityClaimStatuses.DENIED)
        self.assertEqual("unclaimed", self.status())

    def test_revoked_claim_reads_as_not_started(self):
        self.create_claim(status=FacilityClaimStatuses.REVOKED)
        self.assertEqual("unclaimed", self.status())

    def test_new_pending_claim_after_a_denied_one_reads_as_pending(self):
        self.create_claim(status=FacilityClaimStatuses.DENIED)
        self.create_claim(status=FacilityClaimStatuses.PENDING)
        self.assertEqual("pending", self.status())

    def test_approved_claim_outranks_a_later_pending_one(self):
        self.create_claim(status=FacilityClaimStatuses.APPROVED)
        self.create_claim(status=FacilityClaimStatuses.PENDING)
        self.assertEqual("claimed", self.status())

    def test_approved_claim_outranks_an_earlier_pending_one(self):
        self.create_claim(status=FacilityClaimStatuses.PENDING)
        self.create_claim(status=FacilityClaimStatuses.APPROVED)
        self.assertEqual("claimed", self.status())

    def test_closed_facility_keeps_its_claim_status(self):
        self.facility.is_closed = True
        self.facility.save()
        self.create_claim(status=FacilityClaimStatuses.APPROVED)
        self.assertEqual("claimed", self.status())


class ClaimCampaignDashboardFreshnessTest(ClaimCampaignRosterBaseTest):
    url = "/api/claim-campaigns/"

    @override_switch("claim_campaigns", active=True)
    def test_supplier_claimed_after_creation_shows_as_claimed(self):
        self.add_to_roster(self.campaign, self.facility)

        [supplier] = self.client.get(self.url).json()[0]["suppliers"]
        self.assertEqual("unclaimed", supplier["claim_status"])

        claim = self.create_claim(status=FacilityClaimStatuses.PENDING)
        [supplier] = self.client.get(self.url).json()[0]["suppliers"]
        self.assertEqual("pending", supplier["claim_status"])

        claim.status = FacilityClaimStatuses.APPROVED
        claim.save()
        [supplier] = self.client.get(self.url).json()[0]["suppliers"]
        self.assertEqual("claimed", supplier["claim_status"])

        claim.status = FacilityClaimStatuses.REVOKED
        claim.save()
        [supplier] = self.client.get(self.url).json()[0]["suppliers"]
        self.assertEqual("unclaimed", supplier["claim_status"])


class RemovedListItemsTest(ClaimCampaignRosterBaseTest):
    """
    Suppliers the brand has removed from a list stop being candidates
    (and leave a v1 list-based roster).
    """

    candidates_url = "/api/claim-campaigns/candidates/"
    url = "/api/claim-campaigns/"

    def candidate_ids(self):
        response = self.client.get(
            self.candidates_url, {"list": self.facility_list.id}
        )
        return [s["os_id"] for s in response.json()["suppliers"]]

    def dissociate_other_facility(self):
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.other_facility,
            facility_list_item=self.other_item,
            confidence=1,
            results={},
            is_active=False,
        )

    @override_flag(SELF_SERVE, active=True)
    @override_switch("claim_campaigns", active=True)
    def test_dissociated_supplier_is_not_a_candidate(self):
        self.dissociate_other_facility()
        self.assertEqual([self.facility.id], self.candidate_ids())

    @override_flag(SELF_SERVE, active=True)
    @override_switch("claim_campaigns", active=True)
    def test_removed_item_is_not_a_candidate(self):
        self.other_item.status = FacilityListItem.ITEM_REMOVED
        self.other_item.save()
        self.assertEqual([self.facility.id], self.candidate_ids())

    @override_switch("claim_campaigns", active=True)
    def test_dissociated_supplier_leaves_list_based_roster(self):
        self.dissociate_other_facility()
        [campaign] = self.client.get(self.url).json()
        self.assertEqual(
            [self.facility.id], [s["os_id"] for s in campaign["suppliers"]]
        )


class MergedSupplierTest(ClaimCampaignRosterBaseTest):
    """
    A roster supplier that is merged into another production location
    stays in the campaign under its surviving OS ID.
    """

    def setUp(self):
        super().setUp()
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )
        self.superuser = User.objects.create_superuser(
            email="super@example.com", password="example123"
        )

    def tearDown(self):
        post_delete.connect(
            location_post_delete_handler_for_opensearch, Facility
        )
        super().tearDown()

    def roster(self, campaign):
        return list(
            campaign.suppliers.order_by("id").values_list(
                "facility_id", flat=True
            )
        )

    def invite(self, facility):
        return FacilityClaimInvite.objects.create(
            facility=facility,
            sent_by_user=self.user,
            recipient_email="contact@supplier.com",
        )

    def test_move_repoints_roster_and_invites(self):
        self.add_to_roster(self.campaign, self.other_facility)
        invite = self.invite(self.other_facility)

        move_campaign_suppliers(self.other_facility, self.facility)

        self.assertEqual([self.facility.id], self.roster(self.campaign))
        invite.refresh_from_db()
        self.assertEqual(self.facility.id, invite.facility_id)

    def test_move_does_not_duplicate_a_supplier_already_on_roster(self):
        self.add_to_roster(self.campaign, self.facility, self.other_facility)
        second = ClaimCampaign.objects.create(
            contributor=self.contributor,
            name="Second",
            code="EXAMPLE-SECOND-26",
        )
        self.add_to_roster(second, self.other_facility)

        move_campaign_suppliers(self.other_facility, self.facility)

        self.assertEqual([self.facility.id], self.roster(self.campaign))
        self.assertEqual([self.facility.id], self.roster(second))

    @override_switch("claim_campaigns", active=True)
    def test_merge_endpoint_keeps_the_supplier_in_the_campaign(self):
        self.add_to_roster(self.campaign, self.other_facility)
        self.client.login(email="super@example.com", password="example123")

        response = self.client.post(
            "/api/facilities/merge/?target={}&merge={}".format(
                self.facility.id, self.other_facility.id
            )
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual([self.facility.id], self.roster(self.campaign))
        self.assertEqual(1, ClaimCampaignSupplier.objects.count())
