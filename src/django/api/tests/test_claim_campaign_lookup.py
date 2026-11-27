from api.models import ClaimCampaign, FacilityClaim, User
from api.tests.test_claim_campaign import (
    ClaimCampaignBaseTest,
    grant_campaign_access,
)
from waffle.testutils import override_switch


class ClaimCampaignLookupTest(ClaimCampaignBaseTest):
    """
    GET /api/claim-campaigns/lookup/?code= tells the claim form whether to
    show the campaign banner. Claimants are not campaign owners, so it
    needs neither the access flag nor a contributor.
    """

    def setUp(self):
        super().setUp()

        self.claimant = User.objects.create(email="claimant@example.com")
        self.claimant.set_password("example123")
        self.claimant.save()
        self.client.login(email=self.claimant.email, password="example123")

        self.url = "/api/claim-campaigns/lookup/"

    def lookup(self, code):
        return self.client.get(self.url, {"code": code})

    @override_switch("claim_campaigns", active=True)
    def test_active_code_is_active(self):
        response = self.lookup("EXAMPLE-FRESH-26")
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {"code": "EXAMPLE-FRESH-26", "active": True}, response.json()
        )

    @override_switch("claim_campaigns", active=True)
    def test_code_is_matched_case_insensitively(self):
        response = self.lookup("  example-fresh-26 ")
        self.assertEqual(
            {"code": "EXAMPLE-FRESH-26", "active": True}, response.json()
        )

    @override_switch("claim_campaigns", active=True)
    def test_closed_campaign_is_not_active(self):
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()

        self.assertFalse(self.lookup("EXAMPLE-FRESH-26").json()["active"])

    @override_switch("claim_campaigns", active=True)
    def test_unknown_or_malformed_code_is_not_active(self):
        for code in ("UNKNOWN-26", "not a code!", "A" * 51):
            response = self.lookup(code)
            self.assertEqual(200, response.status_code)
            self.assertFalse(response.json()["active"])

    @override_switch("claim_campaigns", active=True)
    def test_says_nothing_about_the_campaign(self):
        body = self.lookup("EXAMPLE-FRESH-26").json()
        self.assertEqual({"code", "active"}, set(body))

    @override_switch("claim_campaigns", active=True)
    def test_missing_code_is_a_bad_request(self):
        self.assertEqual(400, self.client.get(self.url).status_code)

    @override_switch("claim_campaigns", active=True)
    def test_requires_authentication(self):
        self.client.logout()
        self.assertEqual(401, self.lookup("EXAMPLE-FRESH-26").status_code)

    @override_switch("claim_campaigns", active=False)
    def test_not_found_while_switch_is_off(self):
        self.assertEqual(404, self.lookup("EXAMPLE-FRESH-26").status_code)


class ClaimCampaignNoContributorTest(ClaimCampaignBaseTest):
    def setUp(self):
        super().setUp()

        self.no_contributor_user = User.objects.create(
            email="nocontributor@example.com"
        )
        self.no_contributor_user.set_password("example123")
        self.no_contributor_user.save()
        grant_campaign_access(self.no_contributor_user, self_serve=True)
        self.client.login(
            email=self.no_contributor_user.email, password="example123"
        )

    @override_switch("claim_campaigns", active=True)
    def test_list_is_forbidden_without_a_contributor(self):
        response = self.client.get("/api/claim-campaigns/")
        self.assertEqual(403, response.status_code)

    @override_switch("claim_campaigns", active=True)
    def test_candidates_are_forbidden_without_a_contributor(self):
        response = self.client.get("/api/claim-campaigns/candidates/")
        self.assertEqual(403, response.status_code)

    @override_switch("claim_campaigns", active=True)
    def test_create_is_forbidden_without_a_contributor(self):
        response = self.client.post(
            "/api/claim-campaigns/",
            {"name": "Mine", "os_ids": [self.facility.id]},
            format="json",
        )
        self.assertEqual(403, response.status_code)

    @override_switch("claim_campaigns", active=True)
    def test_lookup_works_without_a_contributor(self):
        response = self.client.get(
            "/api/claim-campaigns/lookup/", {"code": "EXAMPLE-FRESH-26"}
        )
        self.assertEqual(200, response.status_code)


@override_switch("claim_campaigns", active=True)
class ClaimCampaignCodeOnClaimTest(ClaimCampaignBaseTest):
    def setUp(self):
        super().setUp()

        self.user.set_password("example123")
        self.user.save()
        self.list_item.facility = self.facility
        self.list_item.save()
        self.client.login(email=self.user.email, password="example123")

        self.claim_data = {
            "your_name": "John Doe",
            "your_title": "Facility Manager",
            "your_business_website": "https://example.com",
            "business_website": "https://facility.com",
            "business_linkedin_profile": "",
            "facility_description": "description",
        }

    def post_claim(self, **extra):
        return self.client.post(
            f"/api/facilities/{self.facility.id}/claim/",
            {**self.claim_data, **extra},
        )

    @override_switch("claim_a_facility", active=True)
    def test_over_long_code_does_not_block_the_claim(self):
        response = self.post_claim(campaign="X" * 200)
        self.assertEqual(200, response.status_code)

        claim = FacilityClaim.objects.get(facility=self.facility)
        # Falls back to roster attribution, not via the link.
        self.assertEqual(self.campaign, claim.campaign)
        self.assertFalse(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_lower_case_code_is_attributed_via_link(self):
        response = self.post_claim(campaign="example-fresh-26")
        self.assertEqual(200, response.status_code)

        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertEqual(self.campaign, claim.campaign)
        self.assertTrue(claim.via_link)

    @override_switch("claim_a_facility", active=True)
    def test_claimant_endpoint_omits_campaign_code(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="Name",
            company_name="Test",
            facility_description="description",
            status="APPROVED",
            campaign=self.campaign,
        )

        response = self.client.get("/api/facilities/claimed/")
        self.assertEqual(200, response.status_code)

        [row] = response.json()
        self.assertNotIn("campaign_code", row)
