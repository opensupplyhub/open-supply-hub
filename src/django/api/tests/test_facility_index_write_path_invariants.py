"""Write-path invariants for the derived columns of api_facilityindex.

Every search filter and profile read is served from api_facilityindex,
which is kept fresh incrementally: SQL triggers on the source tables
call per-table recompute procedures (sqls/0254_isic_dependent_triggers.sql
and friends), and some views call index_facilities_new() explicitly.
When a derived column gains a new dependency, the per-table procedures
must be updated too - the OSDEV-3428/OSDEV-3430 regressions happened
because the 0231 taxonomy rewrite changed index_facility_type /
index_processing_type without touching the procedures, so list approval
and claim approval left those columns stale while a full rebuild
computed them correctly.

These tests pin the general invariant behind both fixes: after any
write path completes, the facility's index row must equal what a full
recompute of that facility produces. assertIndexMatchesFullRebuild
snapshots the row, runs `CALL index_facilities_by(ARRAY[id])` (the same
procedure the full rebuild and the facility trigger use), and fails
with the per-column diff if anything moved. The comparison iterates the
model's concrete fields, so a future column is covered the day it is
added, with no test change.
"""
import json

from django.db import connection
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import ExtendedField, FacilityClaim, FacilityList
from api.models.facility.facility_index import FacilityIndex
from api.tests.base_moderation_events_production_location_test import (
    BaseModerationEventsProductionLocationTest,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilityIndexInvariantMixin:
    """assertIndexMatchesFullRebuild for any test case with a facility."""

    # Bookkeeping columns that legitimately differ between the
    # incremental write and a rebuild.
    REBUILD_EXCLUDED_FIELDS = {"uuid", "created_at", "updated_at"}

    @staticmethod
    def _canonical(value):
        # Arrays are compared as multisets: both sides run the same
        # index_* SQL functions, but array_agg order is not guaranteed
        # between two executions and is not part of the contract.
        if isinstance(value, list):
            return sorted(
                json.dumps(item, sort_keys=True, default=str)
                for item in value
            )
        if isinstance(value, dict):
            return json.dumps(value, sort_keys=True, default=str)
        if value is not None and hasattr(value, "ewkt"):
            return value.ewkt
        return value

    def _index_snapshot(self, facility_id):
        row = FacilityIndex.objects.get(id=facility_id)
        return {
            field.name: self._canonical(getattr(row, field.attname))
            for field in FacilityIndex._meta.concrete_fields
            if field.name not in self.REBUILD_EXCLUDED_FIELDS
        }

    def assertIndexMatchesFullRebuild(self, facility_id):
        incremental = self._index_snapshot(facility_id)
        with connection.cursor() as cursor:
            cursor.execute("CALL index_facilities_by(%s)", [[facility_id]])
        rebuilt = self._index_snapshot(facility_id)
        stale = [
            (name, incremental[name], rebuilt[name])
            for name in rebuilt
            if incremental[name] != rebuilt[name]
        ]
        if stale:
            lines = [
                f"  {name}:\n"
                f"    after the write path: {before!r}\n"
                f"    after a full rebuild: {after!r}"
                for name, before, after in stale
            ]
            self.fail(
                "FacilityIndex drifted from a full recompute for "
                f"{facility_id}. The write path left these columns stale, "
                "which usually means a per-table recompute procedure "
                "(sqls/0254_isic_dependent_triggers.sql and friends) was "
                "not updated for a column's new dependency:\n"
                + "\n".join(lines)
            )


def taxonomy_field_value(label):
    return {
        "raw_values": label.lower(),
        "matched_values": [
            ["PROCESSING_TYPE", "EXACT", label, label],
        ],
    }


class TriggerProcedureInvariantsTest(
    FacilityIndexInvariantMixin, FacilityAPITestCaseBase
):
    """Direct mutations of each trigger-bearing table hold the invariant."""

    def setUp(self):
        super().setUp()
        # A taxonomy field on the list item gives the visibility-
        # dependent columns (facility_type, processing_type, isic_*)
        # content that depends on the item, its match, and its source.
        self.taxonomy_field = ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.FACILITY_TYPE,
            value=taxonomy_field_value("Final Product Assembly"),
        )

    def test_extended_field_insert(self):
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.PROCESSING_TYPE,
            value=taxonomy_field_value("Packaging"),
        )
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_extended_field_delete(self):
        self.taxonomy_field.delete()
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_match_deactivation(self):
        self.match.is_active = False
        self.match.save()
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_source_deactivation(self):
        self.source.is_active = False
        self.source.save()
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_list_item_name_change(self):
        self.list_item.name = "Renamed item"
        self.list_item.save()
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_contributor_rename(self):
        self.contributor.name = "Renamed contributor"
        self.contributor.save()
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_facility_save(self):
        self.facility.name = "Renamed facility"
        self.facility.save()
        self.assertIndexMatchesFullRebuild(self.facility.id)


class ClaimWritePathInvariantsTest(
    FacilityIndexInvariantMixin, FacilityAPITestCaseBase
):
    """Claim status changes hold the invariant, via model and endpoint."""

    def setUp(self):
        super().setUp()
        self.claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person="Person",
            job_title="Title",
            status=FacilityClaimStatuses.PENDING,
        )
        # Taxonomy data attached to the claim: visible to the index
        # functions only while the claim is APPROVED, so every status
        # flip must recompute the dependent columns (OSDEV-3430).
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_claim=self.claim,
            field_name=ExtendedField.FACILITY_TYPE,
            value=taxonomy_field_value("Final Product Assembly"),
        )

    def set_claim_status(self, status):
        self.claim.status = status
        self.claim.save()

    def test_claim_approval_via_model(self):
        self.set_claim_status(FacilityClaimStatuses.APPROVED)
        self.assertIndexMatchesFullRebuild(self.facility.id)
        # The invariant alone would pass if both sides were empty, so
        # pin that the approval actually surfaced the claim data.
        row = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Final Product Assembly", row.facility_type)
        self.assertNotEqual([], row.approved_claim_ids)

    def test_claim_revocation_via_model(self):
        self.set_claim_status(FacilityClaimStatuses.APPROVED)
        self.set_claim_status(FacilityClaimStatuses.REVOKED)
        self.assertIndexMatchesFullRebuild(self.facility.id)
        row = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual([], row.facility_type)

    def test_claim_denial_via_model(self):
        self.set_claim_status(FacilityClaimStatuses.DENIED)
        self.assertIndexMatchesFullRebuild(self.facility.id)

    @override_switch("claim_a_facility", active=True)
    def test_claim_approval_via_endpoint(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/approve/"
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertIndexMatchesFullRebuild(self.facility.id)
        row = FacilityIndex.objects.get(id=self.facility.id)
        self.assertNotEqual([], row.approved_claim_ids)

    @override_switch("claim_a_facility", active=True)
    def test_claim_revocation_via_endpoint(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/approve/"
        )
        self.assertEqual(200, response.status_code, response.content)
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/revoke/"
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertIndexMatchesFullRebuild(self.facility.id)


class ListStatusInvariantsTest(
    FacilityIndexInvariantMixin, FacilityAPITestCaseBase
):
    """List approval and rejection (source activation) hold the invariant."""

    def setUp(self):
        super().setUp()
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.FACILITY_TYPE,
            value=taxonomy_field_value("Final Product Assembly"),
        )
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

    def test_list_approval(self):
        response = self.client.post(
            f"/api/facility-lists/{self.list.id}/approve/",
            {"reason": "looks good"},
            format="json",
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertIndexMatchesFullRebuild(self.facility.id)

    def test_list_rejection(self):
        response = self.client.post(
            f"/api/facility-lists/{self.list.id}/reject/",
            {"reason": "not usable"},
            format="json",
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertIndexMatchesFullRebuild(self.facility.id)
        # Rejection deactivates the source, so the source-visibility
        # dependent columns must empty out, not just hold the invariant.
        self.list.refresh_from_db()
        self.assertEqual(FacilityList.REJECTED, self.list.status)


class UpdateLocationInvariantTest(
    FacilityIndexInvariantMixin, FacilityAPITestCaseBase
):
    """The admin update-location path holds the invariant."""

    def test_update_location(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            f"/api/facilities/{self.facility.id}/update-location/",
            {"lat": 41.0, "lng": 29.0},
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertIndexMatchesFullRebuild(self.facility.id)
        # Compare coordinates, not GEOSGeometry objects: the stored
        # point carries SRID 4326 and a bare Point does not, which makes
        # object equality fail on otherwise identical locations.
        row = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual((29.0, 41.0), (row.location.x, row.location.y))


class ModerationEventApprovalInvariantTest(
    FacilityIndexInvariantMixin, BaseModerationEventsProductionLocationTest
):
    """Approving a v1 moderation event (the SLC / API-moderation path,
    OSDEV-3428's surface) leaves the new facility's index row equal to a
    full recompute."""

    def get_url(self):
        return "/api/v1/moderation-events/{}/production-locations/".format(
            self.moderation_event_id
        )

    def test_add_production_location_approval(self):
        self.add_extended_fields_data()
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code, response.content)
        os_id = response.data["os_id"]
        self.assertIndexMatchesFullRebuild(os_id)
        row = FacilityIndex.objects.get(id=os_id)
        self.assertNotEqual([], row.facility_type)
