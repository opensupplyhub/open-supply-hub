from api.models import (
    ClaimCampaign,
    ClaimCampaignSupplier,
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.services.claim_campaign_service import resolve_claim_campaign
from api.tests.test_claim_campaign_roster import (
    SELF_SERVE,
    ClaimCampaignRosterBaseTest,
)
from waffle.testutils import override_flag, override_switch

from django.contrib.gis.geos import Point

URL = "/api/claim-campaigns/"
CANDIDATES_URL = "/api/claim-campaigns/candidates/"


class ApiOnlyContributorBaseTest(ClaimCampaignRosterBaseTest):
    """
    A second brand that has never uploaded a list: it added its
    suppliers one at a time through the API (one SINGLE source per
    submission), the way API-only contributors do.
    """

    def setUp(self):
        super().setUp()
        self.client.logout()

        self.api_user = User.objects.create(email="api@example.com")
        self.api_user.set_password(self.password)
        self.api_user.save()
        self.api_contributor = Contributor.objects.create(
            admin=self.api_user,
            name="Api Brand",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.api_facility_a = self.submit_through_api("Alpha", 10)
        self.api_facility_b = self.submit_through_api(
            "Beta", 11, is_public=False
        )
        # Matched to a facility someone else created.
        self.submit_through_api("Alpha again", 12, facility=self.facility)

        self.client.login(email=self.api_user.email, password=self.password)

    def submit_through_api(self, name, x, is_public=True, facility=None):
        source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=is_public,
            contributor=self.api_contributor,
        )
        item = FacilityListItem.objects.create(
            name=name,
            address=f"{name} address",
            country_code="VN",
            sector=["Apparel"],
            row_index=0,
            geocoded_point=Point(x, x),
            status=FacilityListItem.MATCHED,
            source=source,
        )
        if facility is None:
            facility = Facility.objects.create(
                name=name,
                address=f"{name} address",
                country_code="VN",
                location=Point(x, x),
                created_from=item,
            )
        item.facility = facility
        item.save()
        return facility


@override_switch("claim_campaigns", active=True)
@override_flag(SELF_SERVE, active=True)
class ApiOnlyContributorCampaignTest(ApiOnlyContributorBaseTest):
    def test_candidates_offer_api_submissions_as_one_source(self):
        entries = self.client.get(CANDIDATES_URL).json()
        self.assertEqual(1, len(entries))
        entry = entries[0]
        self.assertEqual("api", entry["id"])
        self.assertEqual("api", entry["kind"])
        self.assertEqual("Locations added through the API", entry["name"])
        self.assertEqual(3, entry["supplier_count"])
        # One of the submissions is private, so the entry is too.
        self.assertFalse(entry["is_public"])
        self.assertFalse(entry["pending"])

    def test_api_source_lists_suppliers_in_submission_order(self):
        response = self.client.get(CANDIDATES_URL, {"list": "api"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [self.api_facility_a.id, self.api_facility_b.id, self.facility.id],
            [s["os_id"] for s in response.json()["suppliers"]],
        )

    def test_create_campaign_from_api_submissions(self):
        response = self.client.post(
            URL,
            {
                "name": "API onboarding",
                "list_id": "api",
                "os_ids": [self.api_facility_a.id, self.api_facility_b.id],
            },
            format="json",
        )
        self.assertEqual(201, response.status_code)
        campaign = ClaimCampaign.objects.get(name="API onboarding")
        self.assertEqual(self.api_contributor, campaign.contributor)
        self.assertEqual(
            {self.api_facility_a.id, self.api_facility_b.id},
            set(campaign.suppliers.values_list("facility_id", flat=True)),
        )
        self.assertEqual(
            (campaign, False),
            resolve_claim_campaign(self.api_facility_a, None),
        )

    def test_create_refuses_os_ids_not_submitted_through_the_api(self):
        response = self.client.post(
            URL,
            {
                "name": "API onboarding",
                "list_id": "api",
                "os_ids": [self.api_facility_a.id, self.other_facility.id],
            },
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(self.other_facility.id, str(response.json()))
        self.assertFalse(ClaimCampaign.objects.filter(
            contributor=self.api_contributor).exists())

    def test_removed_and_inactive_api_submissions_are_left_out(self):
        Source.objects.filter(
            contributor=self.api_contributor,
            facilitylistitem__facility=self.api_facility_b,
        ).update(is_active=False)

        entry = self.client.get(CANDIDATES_URL).json()[0]
        self.assertEqual(2, entry["supplier_count"])
        self.assertTrue(entry["is_public"])

    def test_search_works_for_api_only_contributors(self):
        response = self.client.get(
            f"{CANDIDATES_URL}search/", {"q": "Alpha"}
        )
        self.assertEqual(200, response.status_code)

    def test_list_contributor_without_api_submissions_gets_no_api_entry(self):
        self.client.logout()
        self.client.login(email=self.user.email, password=self.password)
        entries = self.client.get(CANDIDATES_URL).json()
        self.assertNotIn("api", [entry["id"] for entry in entries])
        self.assertEqual(
            404,
            self.client.get(CANDIDATES_URL, {"list": "api"}).status_code,
        )


@override_switch("claim_campaigns", active=True)
class ApiOnlyContributorStaffCampaignTest(ApiOnlyContributorBaseTest):
    def test_staff_campaign_without_roster_covers_api_submissions(self):
        """
        A campaign OS Hub staff set up with no roster uses everything
        the brand contributed, which includes API submissions.
        """
        ClaimCampaign.objects.create(
            contributor=self.api_contributor, name="Staff", code="API-26"
        )
        campaigns = self.client.get(URL).json()
        self.assertEqual(
            {self.api_facility_a.id, self.api_facility_b.id, self.facility.id},
            {s["os_id"] for s in campaigns[0]["suppliers"]},
        )


@override_switch("claim_campaigns", active=True)
@override_flag(SELF_SERVE, active=True)
class PendingListCandidatesTest(ClaimCampaignRosterBaseTest):
    def entry(self, list_id):
        return next(
            e
            for e in self.client.get(CANDIDATES_URL).json()
            if e["id"] == list_id
        )

    def test_approved_list_reports_its_matched_suppliers(self):
        self.facility_list.status = FacilityList.APPROVED
        self.facility_list.save()
        entry = self.entry(self.facility_list.id)
        self.assertFalse(entry["pending"])
        self.assertEqual(2, entry["supplier_count"])

    def test_list_in_moderation_is_pending(self):
        pending_list = FacilityList.objects.create(
            header="header", file_name="new", name="New upload"
        )
        source = Source.objects.create(
            facility_list=pending_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        FacilityListItem.objects.create(
            name="Waiting",
            address="Waiting address",
            country_code="BD",
            sector=["Apparel"],
            row_index=0,
            status=FacilityListItem.UPLOADED,
            source=source,
        )
        entry = self.entry(pending_list.id)
        self.assertTrue(entry["pending"])
        self.assertEqual(0, entry["supplier_count"])

    def test_approved_list_still_processing_is_pending(self):
        self.facility_list.status = FacilityList.APPROVED
        self.facility_list.save()
        FacilityListItem.objects.create(
            name="Geocoding",
            address="Somewhere",
            country_code="BD",
            sector=["Apparel"],
            row_index=3,
            status=FacilityListItem.PARSED,
            source=self.source,
        )
        self.assertTrue(self.entry(self.facility_list.id)["pending"])


@override_switch("claim_campaigns", active=True)
class CloseCampaignTest(ClaimCampaignRosterBaseTest):
    def close_url(self, campaign):
        return f"{URL}{campaign.id}/close/"

    @override_flag(SELF_SERVE, active=False)
    def test_owner_closes_a_campaign_without_the_self_serve_flag(self):
        response = self.client.post(self.close_url(self.campaign))
        self.assertEqual(200, response.status_code)
        self.assertEqual("CLOSED", response.json()["status"])
        self.campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.CLOSED, self.campaign.status)

    def test_closed_campaign_stops_attributing_claims(self):
        ClaimCampaignSupplier.objects.create(
            campaign=self.campaign, facility=self.facility
        )
        self.client.post(self.close_url(self.campaign))
        self.assertEqual(
            (None, False), resolve_claim_campaign(self.facility, None)
        )
        self.assertEqual(
            (None, False),
            resolve_claim_campaign(self.facility, self.campaign.code),
        )

    def test_closing_twice_is_harmless(self):
        self.client.post(self.close_url(self.campaign))
        response = self.client.post(self.close_url(self.campaign))
        self.assertEqual(200, response.status_code)
        self.assertEqual("CLOSED", response.json()["status"])

    def test_another_brands_campaign_cannot_be_closed(self):
        other_user = User.objects.create(email="other@example.com")
        other = Contributor.objects.create(
            admin=other_user,
            name="Other brand",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        theirs = ClaimCampaign.objects.create(
            contributor=other, name="Theirs", code="THEIRS-26"
        )
        response = self.client.post(self.close_url(theirs))
        self.assertEqual(404, response.status_code)
        theirs.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.ACTIVE, theirs.status)

    def test_anonymous_user_cannot_close(self):
        self.client.logout()
        response = self.client.post(self.close_url(self.campaign))
        self.assertIn(response.status_code, (401, 403))

    @override_switch("claim_campaigns", active=False)
    def test_close_is_hidden_when_the_switch_is_off(self):
        response = self.client.post(self.close_url(self.campaign))
        self.assertEqual(404, response.status_code)
