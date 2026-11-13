from unittest.mock import patch

from api.admin import ClaimCampaignAdminForm
from api.models import ClaimCampaign, FacilityList
from api.tests.test_claim_campaign_roster import (
    SELF_SERVE,
    ClaimCampaignRosterBaseTest,
)
from waffle.testutils import override_flag, override_switch

URL = "/api/claim-campaigns/"
CANDIDATES_URL = "/api/claim-campaigns/candidates/"
# The brand's list has two matched facilities, so a limit of one makes
# it too large without creating thousands of rows.
LIMIT = "api.services.claim_campaign_service.MAX_LIST_FACILITIES"


@override_switch("claim_campaigns", active=True)
@override_flag(SELF_SERVE, active=True)
class TooLargeListCandidatesTest(ClaimCampaignRosterBaseTest):
    def setUp(self):
        super().setUp()
        self.facility_list.status = FacilityList.APPROVED
        self.facility_list.save()

    def entry(self):
        return next(
            e
            for e in self.client.get(CANDIDATES_URL).json()
            if e["id"] == self.facility_list.id
        )

    def list_url(self):
        return f"{CANDIDATES_URL}?list={self.facility_list.id}"

    def test_list_within_the_limit_can_be_opened(self):
        entry = self.entry()
        self.assertFalse(entry["too_large"])
        self.assertEqual(200, self.client.get(self.list_url()).status_code)

    @patch(LIMIT, 2)
    def test_list_exactly_at_the_limit_can_be_opened(self):
        entry = self.entry()
        self.assertFalse(entry["too_large"])
        self.assertEqual(200, self.client.get(self.list_url()).status_code)

    @patch(LIMIT, 1)
    def test_list_over_the_limit_is_marked_and_cannot_be_opened(self):
        entry = self.entry()
        self.assertTrue(entry["too_large"])
        self.assertEqual(2, entry["supplier_count"])

        response = self.client.get(self.list_url())
        self.assertEqual(400, response.status_code)
        self.assertIn("Use search", str(response.json()))

    @patch(LIMIT, 1)
    def test_campaign_cannot_be_created_from_a_list_over_the_limit(self):
        response = self.client.post(
            URL,
            {
                "name": "Too large",
                "list_id": self.facility_list.id,
                "os_ids": [self.facility.id],
            },
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("list_id", response.json())
        self.assertFalse(
            ClaimCampaign.objects.filter(name="Too large").exists()
        )

    @patch(LIMIT, 1)
    def test_search_still_works_for_a_brand_with_a_large_list(self):
        response = self.client.post(
            URL,
            {"name": "From search", "os_ids": [self.facility.id]},
            format="json",
        )
        self.assertEqual(201, response.status_code, response.content)


class ClaimCampaignAdminSizeLimitTest(ClaimCampaignRosterBaseTest):
    def form(self, instance=None, **overrides):
        data = {
            "contributor": self.contributor.id,
            "name": "Staff campaign",
            "code": "STAFF-26",
            "status": ClaimCampaign.Status.ACTIVE,
            "uses_roster": False,
            **overrides,
        }
        return ClaimCampaignAdminForm(data=data, instance=instance)

    def test_list_based_campaign_within_the_limit_is_allowed(self):
        self.assertTrue(self.form().is_valid())

    @patch(LIMIT, 1)
    def test_list_based_campaign_over_the_limit_is_refused(self):
        form = self.form()
        self.assertFalse(form.is_valid())
        self.assertIn("chosen suppliers only", str(form.non_field_errors()))

    @patch(LIMIT, 1)
    def test_chosen_suppliers_campaign_is_allowed_for_a_large_brand(self):
        self.assertTrue(self.form(uses_roster=True).is_valid())

    @patch(LIMIT, 1)
    def test_existing_campaign_can_still_be_closed(self):
        form = self.form(
            instance=self.campaign,
            name=self.campaign.name,
            code=self.campaign.code,
            status=ClaimCampaign.Status.CLOSED,
        )
        self.assertTrue(form.is_valid(), form.errors)

    @patch(LIMIT, 1)
    def test_existing_campaign_cannot_be_switched_back_to_all_lists(self):
        self.campaign.uses_roster = True
        self.campaign.save()
        form = self.form(
            instance=self.campaign,
            name=self.campaign.name,
            code=self.campaign.code,
        )
        self.assertFalse(form.is_valid())
