"""
End-to-end scenarios asked about in review (2026-11-09). Each test
names the question it answers.
"""
from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimCampaign,
    ClaimCampaignSupplier,
    Contributor,
    Facility,
    FacilityClaim,
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


@override_switch("claim_campaigns", active=True)
@override_flag(SELF_SERVE, active=True)
class ClaimCampaignScenarioTest(ClaimCampaignRosterBaseTest):
    def setUp(self):
        super().setUp()
        # The brand's list holds self.facility and self.other_facility.
        self.api_facility = self.submit_through_api("Api only", 5)

    # Helpers

    def submit_through_api(self, name, x, facility=None, status=None):
        source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            name=name,
            address=f"{name} address",
            country_code="VN",
            sector=["Apparel"],
            row_index=0,
            geocoded_point=Point(x, x),
            status=status or FacilityListItem.MATCHED,
            source=source,
        )
        if status not in (None, FacilityListItem.MATCHED):
            # Not matched yet: no production location to attach.
            return None
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

    def entries(self):
        return {e["id"]: e for e in self.client.get(CANDIDATES_URL).json()}

    def create(self, name, os_ids, list_id=None):
        payload = {"name": name, "os_ids": os_ids}
        if list_id is not None:
            payload["list_id"] = list_id
        response = self.client.post(URL, payload, format="json")
        self.assertEqual(201, response.status_code, response.content)
        return ClaimCampaign.objects.get(pk=response.json()["id"])

    def campaign_rows(self, campaign):
        data = next(
            c for c in self.client.get(URL).json() if c["id"] == campaign.id
        )
        return {s["os_id"]: s for s in data["suppliers"]}

    def claim(self, facility, status):
        return FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=facility,
            contact_person="Name",
            company_name="Test",
            facility_description="description",
            status=status,
        )

    # (1) A brand with both uploaded lists and API submissions

    def test_1_brand_with_lists_and_api_uploads_sees_both_sources(self):
        # The same production location sent both ways appears in both.
        self.submit_through_api("Also on list", 6, facility=self.facility)

        entries = self.entries()
        self.assertEqual(2, entries[self.facility_list.id]["supplier_count"])
        self.assertEqual(2, entries["api"]["supplier_count"])

        api_rows = self.client.get(CANDIDATES_URL, {"list": "api"}).json()
        self.assertEqual(
            [self.api_facility.id, self.facility.id],
            [s["os_id"] for s in api_rows["suppliers"]],
        )
        # A list-only OS ID can't be sent as an API pick, and vice versa.
        response = self.client.post(
            URL,
            {
                "name": "Mixed",
                "list_id": "api",
                "os_ids": [self.other_facility.id],
            },
            format="json",
        )
        self.assertEqual(400, response.status_code)

    # (3) A facility that isn't claimed, on several campaigns

    def test_3_unclaimed_facility_on_two_campaigns(self):
        first = self.create("First", [self.facility.id], self.facility_list.id)
        second = self.create(
            "Second", [self.facility.id], self.facility_list.id
        )

        # Both dashboards list it as not started.
        self.assertEqual(
            "unclaimed", self.campaign_rows(first)[self.facility.id][
                "claim_status"]
        )
        self.assertEqual(
            "unclaimed", self.campaign_rows(second)[self.facility.id][
                "claim_status"]
        )
        # A claim through one campaign's link counts for that campaign;
        # a claim without a link is ambiguous and counts for neither.
        self.assertEqual(
            (second, True),
            resolve_claim_campaign(self.facility, second.code),
        )
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()
        self.assertEqual(
            (None, False), resolve_claim_campaign(self.facility, None)
        )

        # Once claimed, both campaigns show it as claimed.
        self.claim(self.facility, FacilityClaimStatuses.APPROVED)
        self.assertEqual(
            "claimed", self.campaign_rows(first)[self.facility.id][
                "claim_status"]
        )
        self.assertEqual(
            "claimed", self.campaign_rows(second)[self.facility.id][
                "claim_status"]
        )

    # (4) Claimed, then closed or revoked

    def test_4_claimed_then_closed_shows_claimed_and_closed(self):
        campaign = self.create(
            "Close", [self.facility.id], self.facility_list.id
        )
        self.claim(self.facility, FacilityClaimStatuses.APPROVED)
        self.facility.is_closed = True
        self.facility.save()

        row = self.campaign_rows(campaign)[self.facility.id]
        self.assertEqual("claimed", row["claim_status"])
        self.assertTrue(row["is_closed"])

    def test_4_claimed_then_revoked_shows_not_started(self):
        campaign = self.create(
            "Revoke", [self.facility.id], self.facility_list.id
        )
        claim = self.claim(self.facility, FacilityClaimStatuses.APPROVED)
        claim.status = FacilityClaimStatuses.REVOKED
        claim.save()

        row = self.campaign_rows(campaign)[self.facility.id]
        self.assertEqual("unclaimed", row["claim_status"])
        self.assertFalse(row["is_closed"])

    def test_4_revoked_then_closed_shows_not_started_and_closed(self):
        campaign = self.create(
            "Both", [self.facility.id], self.facility_list.id
        )
        self.claim(self.facility, FacilityClaimStatuses.REVOKED)
        self.facility.is_closed = True
        self.facility.save()

        row = self.campaign_rows(campaign)[self.facility.id]
        self.assertEqual("unclaimed", row["claim_status"])
        self.assertTrue(row["is_closed"])

    # (5) API uploads that wait for the brand to confirm a match

    def test_5_api_uploads_waiting_for_confirmation_are_reported(self):
        self.submit_through_api(
            "Maybe", 7, status=FacilityListItem.POTENTIAL_MATCH
        )
        self.submit_through_api(
            "Still geocoding", 8, status=FacilityListItem.PARSED
        )

        entry = self.entries()["api"]
        self.assertEqual(1, entry["supplier_count"])
        self.assertEqual(1, entry["awaiting_confirmation"])
        self.assertTrue(entry["pending"])

    def test_5_api_entry_shows_even_when_nothing_has_matched_yet(self):
        # Switch off the matched API submission from setUp.
        Source.objects.filter(
            contributor=self.contributor, source_type=Source.SINGLE
        ).update(is_active=False)
        self.submit_through_api(
            "Maybe", 7, status=FacilityListItem.POTENTIAL_MATCH
        )

        entry = self.entries()["api"]
        self.assertEqual(0, entry["supplier_count"])
        self.assertEqual(1, entry["awaiting_confirmation"])

    def test_5_list_rows_waiting_for_confirmation_are_reported(self):
        FacilityListItem.objects.create(
            name="Maybe",
            address="Maybe address",
            country_code="BD",
            sector=["Apparel"],
            row_index=9,
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.source,
        )
        entry = self.entries()[self.facility_list.id]
        self.assertEqual(2, entry["supplier_count"])
        self.assertEqual(1, entry["awaiting_confirmation"])

    # (6) One campaign from each source

    def test_6_one_campaign_each_from_a_list_api_uploads_and_a_search(self):
        # A production location another brand contributed, found by
        # searching OS Hub.
        someone_else = Contributor.objects.create(
            admin=User.objects.create(email="else@example.com"),
            name="Someone else",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        item = FacilityListItem.objects.create(
            name="Not mine",
            address="Elsewhere",
            country_code="IN",
            sector=["Apparel"],
            row_index=0,
            status=FacilityListItem.MATCHED,
            source=Source.objects.create(
                source_type=Source.SINGLE,
                is_active=True,
                is_public=True,
                contributor=someone_else,
            ),
        )
        searched = Facility.objects.create(
            name="Not mine",
            address="Elsewhere",
            country_code="IN",
            location=Point(9, 9),
            created_from=item,
        )

        from_list = self.create(
            "From list", [self.other_facility.id], self.facility_list.id
        )
        from_api = self.create("From API", [self.api_facility.id], "api")
        from_search = self.create("From search", [searched.id])

        self.assertEqual(
            {self.other_facility.id}, set(self.campaign_rows(from_list))
        )
        self.assertEqual(
            {self.api_facility.id}, set(self.campaign_rows(from_api))
        )
        self.assertEqual({searched.id}, set(self.campaign_rows(from_search)))
        self.assertEqual(4, len(self.client.get(URL).json()))

    # (7) A campaign closed in Django admin shows closed straight away

    def test_7_campaign_closed_on_the_backend_reads_closed_immediately(self):
        campaign = self.create(
            "Admin closes", [self.facility.id], self.facility_list.id
        )
        ClaimCampaign.objects.filter(pk=campaign.pk).update(
            status=ClaimCampaign.Status.CLOSED
        )
        data = next(
            c for c in self.client.get(URL).json() if c["id"] == campaign.id
        )
        self.assertEqual("CLOSED", data["status"])

    # (8) Suppliers added or removed one at a time in Django admin

    def test_8_supplier_added_in_admin_shows_like_any_other(self):
        campaign = self.create(
            "Admin adds", [self.facility.id], self.facility_list.id
        )
        ClaimCampaignSupplier.objects.create(
            campaign=campaign, facility=self.api_facility
        )
        rows = self.campaign_rows(campaign)
        self.assertEqual({self.facility.id, self.api_facility.id}, set(rows))
        self.assertEqual(
            {"os_id", "name", "country_code", "claim_status", "is_closed",
             "last_invite"},
            set(rows[self.api_facility.id]),
        )
        self.assertEqual(
            (campaign, True),
            resolve_claim_campaign(self.api_facility, campaign.code),
        )

    def test_8_suppliers_removed_one_at_a_time_in_admin(self):
        campaign = self.create(
            "Admin removes",
            [self.facility.id, self.other_facility.id],
            self.facility_list.id,
        )
        ClaimCampaignSupplier.objects.get(
            campaign=campaign, facility=self.facility
        ).delete()
        self.assertEqual(
            {self.other_facility.id}, set(self.campaign_rows(campaign))
        )

        # Removing the last one leaves the campaign empty; it does not
        # fall back to every facility on the brand's lists.
        ClaimCampaignSupplier.objects.filter(campaign=campaign).delete()
        campaign.refresh_from_db()
        self.assertTrue(campaign.uses_roster)
        self.assertEqual({}, self.campaign_rows(campaign))
        self.campaign.status = ClaimCampaign.Status.CLOSED
        self.campaign.save()
        self.assertEqual(
            (None, False), resolve_claim_campaign(self.facility, None)
        )

    def test_8_adding_a_supplier_in_admin_to_a_v1_campaign(self):
        # A staff campaign with no chosen suppliers covers every
        # facility on the brand's lists (v1). Adding one in admin turns
        # it into a chosen-suppliers campaign.
        self.assertFalse(self.campaign.uses_roster)
        self.assertEqual(
            {self.facility.id, self.other_facility.id, self.api_facility.id},
            set(self.campaign_rows(self.campaign)),
        )
        ClaimCampaignSupplier.objects.create(
            campaign=self.campaign, facility=self.facility
        )
        self.campaign.refresh_from_db()
        self.assertTrue(self.campaign.uses_roster)
        self.assertEqual(
            {self.facility.id}, set(self.campaign_rows(self.campaign))
        )
