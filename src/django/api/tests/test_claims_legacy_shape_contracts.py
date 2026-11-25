"""Legacy-shaped rows must not break the claims list endpoint.

Production carries claims older than several schema and process
changes: decisions recorded before deciders were (status_change_by
NULL), claims with no parent company, campaign, or invite, and
facilities whose country codes predate the current code list. The
detail endpoint 500d on exactly such a row (PR 1231,
status_change_by.email on a NULL decider) and its fix added a detail
test; the LIST endpoint serializes the same rows in bulk, where one
bad row poisons the whole moderator dashboard page, and had no
legacy-shape coverage.

These tests build one modern row and several legacy rows and assert
the list serves them all. They complement, not duplicate,
test_facility_claim_admin_dashboard's detail-endpoint tests.
"""
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point

from api.constants import FacilityClaimStatuses
from api.models import Facility, FacilityListItem
from api.tests.claim_fixtures import make_claim
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


# The list action is not switch-gated today (that asymmetry is tracked
# on the ticket); the override is here so these tests keep passing when
# the gate is added.
@override_switch("claim_a_facility", active=True)
class ClaimsListLegacyShapeTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        self.modern_claim = make_claim(
            self.facility,
            self.contributor,
            status=FacilityClaimStatuses.DENIED,
            status_change_by=self.superuser,
            status_change_reason="documented decision",
        )
        # A decision from before deciders were recorded.
        self.legacy_decided_claim = make_claim(
            self.facility,
            self.contributor,
            status=FacilityClaimStatuses.DENIED,
            status_change_reason="decided before deciders were recorded",
        )
        # A facility whose stored country code predates the current
        # code list; the serializer must fall back, not crash. Such a
        # row cannot be built through save() - make_os_id refuses a
        # retired code - which is precisely how legacy rows differ from
        # anything creatable today, so write the column past validation
        # the way history did.
        legacy_item = FacilityListItem.objects.create(
            name="Legacy item",
            address="Legacy address",
            country_code="US",
            sector=["Apparel"],
            row_index=2,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.legacy_country_facility = Facility.objects.create(
            name="Legacy country facility",
            address="Legacy address",
            country_code="US",
            location=Point(0, 0),
            created_from=legacy_item,
        )
        Facility.objects.filter(pk=self.legacy_country_facility.pk).update(
            country_code="AN"
        )
        self.legacy_country_facility.refresh_from_db()
        self.legacy_country_claim = make_claim(
            self.legacy_country_facility,
            self.contributor,
            status=FacilityClaimStatuses.APPROVED,
        )
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

    def rows_by_id(self, response):
        return {row["id"]: row for row in response.data}

    def test_list_serves_legacy_rows_alongside_modern_ones(self):
        response = self.client.get("/api/facility-claims/")
        self.assertEqual(200, response.status_code, response.content)
        rows = self.rows_by_id(response)
        self.assertIn(self.modern_claim.id, rows)
        self.assertIn(self.legacy_decided_claim.id, rows)
        self.assertIn(self.legacy_country_claim.id, rows)

    def test_null_decider_row_renders_null_safe(self):
        response = self.client.get("/api/facility-claims/")
        self.assertEqual(200, response.status_code, response.content)
        row = self.rows_by_id(response)[self.legacy_decided_claim.id]
        self.assertEqual(FacilityClaimStatuses.DENIED, row["status"])
        # A legacy decision carries no decider and no decision date;
        # both must serialize as nulls, not crash.
        self.assertIsNone(row["claim_decision"])

    def test_unknown_country_code_falls_back_to_empty_name(self):
        response = self.client.get("/api/facility-claims/")
        self.assertEqual(200, response.status_code, response.content)
        row = self.rows_by_id(response)[self.legacy_country_claim.id]
        self.assertEqual("", row["facility_country_name"])

    def test_rows_without_campaign_or_notes_render_null_safe(self):
        response = self.client.get("/api/facility-claims/")
        self.assertEqual(200, response.status_code, response.content)
        row = self.rows_by_id(response)[self.modern_claim.id]
        self.assertIsNone(row["campaign_code"])
        self.assertEqual([], row["notes_meta"])

    def test_status_filter_still_matches_legacy_rows(self):
        response = self.client.get("/api/facility-claims/?statuses=DENIED")
        self.assertEqual(200, response.status_code, response.content)
        rows = self.rows_by_id(response)
        self.assertIn(self.legacy_decided_claim.id, rows)
        self.assertNotIn(self.legacy_country_claim.id, rows)
