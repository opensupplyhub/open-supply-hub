from io import StringIO

from api.models import (
    Contributor,
    ExtendedField,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_index_extended_field_list_serializer \
    import FacilityIndexExtendedFieldListSerializer
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point
from django.core.management import call_command


class SourceReassignmentTestBase(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super().setUp()

        self.new_user = User.objects.create(email="new@example.com")
        self.new_contributor = Contributor.objects.create(
            admin=self.new_user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.extended_field = self.create_extended_field(
            list_item=self.list_item,
            contributor=self.contributor,
        )

    def create_extended_field(
        self,
        list_item,
        contributor,
        field_name=ExtendedField.NUMBER_OF_WORKERS,
        value=None,
    ):
        return ExtendedField.objects.create(
            contributor=contributor,
            facility=self.facility,
            facility_list_item=list_item,
            field_name=field_name,
            value=value or {"min": 100, "max": 100},
        )

    def create_single_source(self, contributor):
        source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )
        list_item = FacilityListItem.objects.create(
            name="Single Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
            facility=self.facility,
        )
        return source, list_item

    def indexed_extended_field(self, extended_field):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        for indexed in facility_index.extended_fields:
            if indexed["id"] == extended_field.id:
                return indexed
        return None


class SourceContributorReassignmentTest(SourceReassignmentTestBase):
    """
    Reassigning `Source.contributor` must re-attribute every extended
    field contributed through that source. See OSDEV-2159.
    """

    def test_reassignment_updates_extended_field_contributor(self):
        self.source.contributor = self.new_contributor
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )

    def test_reassignment_updates_facility_index_attribution(self):
        # Facility detail pages and search responses read attribution
        # from the denormalized FacilityIndex, not from the model.
        indexed = self.indexed_extended_field(self.extended_field)
        self.assertIsNotNone(indexed)
        self.assertEqual(self.contributor.id, indexed["contributor"]["id"])

        self.source.contributor = self.new_contributor
        self.source.save()

        indexed = self.indexed_extended_field(self.extended_field)
        self.assertIsNotNone(indexed)
        self.assertEqual(
            self.new_contributor.id,
            indexed["contributor"]["id"],
        )
        self.assertEqual(
            self.new_contributor.name,
            indexed["contributor"]["name"],
        )

    def test_reassignment_updates_serialized_attribution(self):
        self.source.contributor = self.new_contributor
        self.source.save()

        indexed = self.indexed_extended_field(self.extended_field)
        serialized = FacilityIndexExtendedFieldListSerializer(
            [indexed],
            context={
                "user_can_see_detail": True,
                "embed_mode_active": False,
                "masked_contributor_ids": set(),
            },
        ).data[0]

        self.assertEqual(
            self.new_contributor.name,
            serialized["contributor_name"],
        )
        # The serializer exposes the contributor's admin user id as
        # `contributor_id`, not the Contributor pk. See
        # get_contributor_id_from_facilityindex.
        self.assertEqual(self.new_user.id, serialized["contributor_id"])
        self.assertNotEqual(self.user.id, serialized["contributor_id"])

    def test_reassignment_preserves_contribution_date(self):
        # The public record reads "<date> by <contributor>"; only the
        # contributor should change.
        original_updated_at = self.extended_field.updated_at

        self.source.contributor = self.new_contributor
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(original_updated_at, self.extended_field.updated_at)

    def test_reassignment_covers_single_sources(self):
        # SINGLE sources have no facility_list, so the relation has to be
        # resolved through FacilityListItem.source.
        source, list_item = self.create_single_source(self.contributor)
        extended_field = self.create_extended_field(
            list_item=list_item,
            contributor=self.contributor,
        )

        source.contributor = self.new_contributor
        source.save()

        extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            extended_field.contributor_id,
        )

    def test_other_sources_are_not_affected(self):
        _, other_list_item = self.create_single_source(self.contributor)
        other_field = self.create_extended_field(
            list_item=other_list_item,
            contributor=self.contributor,
        )

        self.source.contributor = self.new_contributor
        self.source.save()

        other_field.refresh_from_db()
        self.assertEqual(self.contributor.id, other_field.contributor_id)

    def test_fields_without_a_list_item_are_not_affected(self):
        # Extended fields created from a FacilityClaim carry no list item
        # and must keep the claimant as contributor.
        claim_field = self.create_extended_field(
            list_item=None,
            contributor=self.contributor,
        )

        self.source.contributor = self.new_contributor
        self.source.save()

        claim_field.refresh_from_db()
        self.assertEqual(self.contributor.id, claim_field.contributor_id)

    def test_saving_without_contributor_change_is_a_no_op(self):
        self.source.is_public = False
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_update_fields_without_contributor_skips_reassignment(self):
        self.source.contributor = self.new_contributor
        self.source.save(update_fields=["is_active"])

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_clearing_contributor_does_not_break_extended_fields(self):
        # ExtendedField.contributor is NOT NULL, so a cleared source
        # contributor must be skipped rather than propagated.
        self.source.contributor = None
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_creating_a_source_does_not_reassign(self):
        source, _ = self.create_single_source(self.new_contributor)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )
        self.assertEqual(self.new_contributor.id, source.contributor_id)


class BackfillExtendedFieldContributorsTest(SourceReassignmentTestBase):
    """
    The backfill repairs rows that drifted apart before OSDEV-2159
    shipped. Drift is simulated with a queryset update, which bypasses
    Source.save().
    """

    COMMAND = 'backfill_extended_field_contributors'

    def drift_source_contributor(self, source, contributor):
        Source.objects.filter(pk=source.pk).update(contributor=contributor)
        source.refresh_from_db()

    def test_dry_run_reports_without_writing(self):
        self.drift_source_contributor(self.source, self.new_contributor)

        out = StringIO()
        call_command(self.COMMAND, '--dry-run', stdout=out)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )
        self.assertIn('would_update=1', out.getvalue())

    def test_backfill_repairs_drifted_rows(self):
        self.drift_source_contributor(self.source, self.new_contributor)

        out = StringIO()
        call_command(self.COMMAND, stdout=out)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )
        self.assertIn('updated=1', out.getvalue())

    def test_backfill_updates_facility_index_attribution(self):
        self.drift_source_contributor(self.source, self.new_contributor)

        call_command(self.COMMAND, stdout=StringIO())

        indexed = self.indexed_extended_field(self.extended_field)
        self.assertIsNotNone(indexed)
        self.assertEqual(
            self.new_contributor.id,
            indexed["contributor"]["id"],
        )

    def test_backfill_is_idempotent(self):
        self.drift_source_contributor(self.source, self.new_contributor)
        call_command(self.COMMAND, stdout=StringIO())

        out = StringIO()
        call_command(self.COMMAND, stdout=out)

        self.assertIn('nothing to do', out.getvalue())

    def test_backfill_skips_sources_without_a_contributor(self):
        self.drift_source_contributor(self.source, None)

        call_command(self.COMMAND, stdout=StringIO())

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )
