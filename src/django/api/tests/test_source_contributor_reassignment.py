from io import StringIO
from unittest.mock import patch

from api.admin import SourceAdmin, admin_site
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
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.management import call_command
from django.db.models import F
from django.test import RequestFactory, override_settings


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

    def save_source(self, source, **kwargs):
        """
        Save a source and run the transaction.on_commit callbacks it
        registers. TestCase wraps each test in a transaction that never
        commits, so without this the deferred reassignment would never
        execute.
        """
        with self.captureOnCommitCallbacks(execute=True):
            source.save(**kwargs)

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
        self.save_source(self.source)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )

    def test_reassignment_waits_for_the_enclosing_transaction(self):
        # The chunked update is registered with transaction.on_commit, so
        # nothing is re-attributed until the transaction that changed the
        # source commits (TestCase's never does).
        self.source.contributor = self.new_contributor
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_reassignment_is_chunked(self):
        extra = [
            self.create_extended_field(
                list_item=self.list_item,
                contributor=self.contributor,
                field_name=field_name,
                value={"raw_value": field_name},
            )
            for field_name in (
                ExtendedField.NATIVE_LANGUAGE_NAME,
                ExtendedField.PARENT_COMPANY,
            )
        ]

        self.source.contributor = self.new_contributor
        with patch(
            'api.services.source_service.REASSIGNMENT_CHUNK_SIZE', 1
        ):
            self.save_source(self.source)

        for extended_field in [self.extended_field, *extra]:
            extended_field.refresh_from_db()
            self.assertEqual(
                self.new_contributor.id,
                extended_field.contributor_id,
            )

    def test_out_of_order_callbacks_converge_on_current_contributor(self):
        # Concurrent reassignments queue one callback each, and nothing
        # guarantees execution order across workers. The callback only
        # captures the source pk and every chunk re-reads the current
        # contributor under a row lock, so a stale callback (C2) running
        # after a newer one (C3) must not overwrite the newer value.
        third_user = User.objects.create(email="third@example.com")
        third_contributor = Contributor.objects.create(
            admin=third_user,
            name="test contributor 3",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        with self.captureOnCommitCallbacks() as stale_callbacks:
            self.source.contributor = self.new_contributor
            self.source.save()
        with self.captureOnCommitCallbacks() as newer_callbacks:
            self.source.contributor = third_contributor
            self.source.save()

        # Execute the newer reassignment first, then the stale one.
        for callback in newer_callbacks:
            callback()
        for callback in stale_callbacks:
            callback()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            third_contributor.id,
            self.extended_field.contributor_id,
        )

    def test_reassignment_updates_facility_index_attribution(self):
        # Facility detail pages and search responses read attribution
        # from the denormalized FacilityIndex, not from the model.
        indexed = self.indexed_extended_field(self.extended_field)
        self.assertIsNotNone(indexed)
        self.assertEqual(self.contributor.id, indexed["contributor"]["id"])

        self.source.contributor = self.new_contributor
        self.save_source(self.source)

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
        self.save_source(self.source)

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
        self.save_source(self.source)

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
        self.save_source(source)

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
        self.save_source(self.source)

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
        self.save_source(self.source)

        claim_field.refresh_from_db()
        self.assertEqual(self.contributor.id, claim_field.contributor_id)

    def test_saving_without_contributor_change_is_a_no_op(self):
        self.source.is_public = False
        self.save_source(self.source)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_update_fields_without_contributor_skips_reassignment(self):
        self.source.contributor = self.new_contributor
        self.save_source(self.source, update_fields=["is_active"])

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_clearing_contributor_does_not_break_extended_fields(self):
        # ExtendedField.contributor is NOT NULL, so a cleared source
        # contributor must be skipped rather than propagated.
        self.source.contributor = None
        self.save_source(self.source)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    def test_creating_a_source_does_not_reassign(self):
        with self.captureOnCommitCallbacks(execute=True):
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
        self.assertIn('[DRY-RUN]', out.getvalue())
        self.assertIn('processed=1', out.getvalue())

    def test_backfill_repairs_drifted_rows(self):
        self.drift_source_contributor(self.source, self.new_contributor)

        out = StringIO()
        call_command(self.COMMAND, stdout=out)

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )
        self.assertIn('processed=1', out.getvalue())

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

    def test_backfill_commits_each_batch_separately(self):
        extra = [
            self.create_extended_field(
                list_item=self.list_item,
                contributor=self.contributor,
                field_name=field_name,
                value={"raw_value": field_name},
            )
            for field_name in (
                ExtendedField.NATIVE_LANGUAGE_NAME,
                ExtendedField.PARENT_COMPANY,
                ExtendedField.DUNS_ID,
            )
        ]
        self.drift_source_contributor(self.source, self.new_contributor)

        out = StringIO()
        call_command(self.COMMAND, '--batch-size', '2', stdout=out)

        for extended_field in [self.extended_field, *extra]:
            extended_field.refresh_from_db()
            self.assertEqual(
                self.new_contributor.id,
                extended_field.contributor_id,
            )
        # 4 rows at 2 per batch.
        self.assertIn('batches=2', out.getvalue())

    def test_backfill_resumes_from_start_after_id(self):
        later = self.create_extended_field(
            list_item=self.list_item,
            contributor=self.contributor,
            field_name=ExtendedField.NATIVE_LANGUAGE_NAME,
            value={"raw_value": "name"},
        )
        self.drift_source_contributor(self.source, self.new_contributor)

        call_command(
            self.COMMAND,
            '--start-after-id',
            str(self.extended_field.id),
            stdout=StringIO(),
        )

        self.extended_field.refresh_from_db()
        later.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )
        self.assertEqual(self.new_contributor.id, later.contributor_id)

    def test_backfill_limit_stops_early_and_reports_resume_point(self):
        self.create_extended_field(
            list_item=self.list_item,
            contributor=self.contributor,
            field_name=ExtendedField.NATIVE_LANGUAGE_NAME,
            value={"raw_value": "name"},
        )
        self.drift_source_contributor(self.source, self.new_contributor)

        out = StringIO()
        call_command(self.COMMAND, '--limit', '1', stdout=out)

        self.assertIn('processed=1', out.getvalue())
        self.assertIn(
            f'--start-after-id {self.extended_field.id}',
            out.getvalue(),
        )
        # The remaining row is picked up by a plain re-run.
        call_command(self.COMMAND, stdout=StringIO())
        self.assertFalse(
            ExtendedField.objects
            .exclude(
                contributor=F('facility_list_item__source__contributor')
            )
            .filter(facility_list_item__isnull=False)
            .exists()
        )


class SourceReassignmentDispatchTest(SourceReassignmentTestBase):
    """
    Reassignment is dispatched to AWS Batch when it is configured, so
    the caller (typically a Django admin request) is not blocked for
    the minutes a large list takes. Otherwise it runs inline, exactly
    as before. See OSDEV-3758.
    """

    SUBMIT = 'api.services.source_service._submit_reassignment_batch_job'

    @override_settings(
        BATCH_JOB_QUEUE_NAME='queue', BATCH_JOB_DEF_NAME='job-def')
    @patch(SUBMIT)
    def test_list_source_submits_a_batch_job(self, submit):
        submit.return_value = 'job-1'

        self.source.contributor = self.new_contributor
        self.save_source(self.source)

        submit.assert_called_once_with(self.source.facility_list_id)
        # The re-attribution now belongs to the Batch job; the caller
        # must not have run it.
        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.contributor.id,
            self.extended_field.contributor_id,
        )

    @override_settings(
        BATCH_JOB_QUEUE_NAME='queue', BATCH_JOB_DEF_NAME='job-def')
    @patch(SUBMIT)
    def test_single_source_reassigns_inline(self, submit):
        source, list_item = self.create_single_source(self.contributor)
        field = self.create_extended_field(
            list_item=list_item,
            contributor=self.contributor,
        )

        source.contributor = self.new_contributor
        self.save_source(source)

        submit.assert_not_called()
        field.refresh_from_db()
        self.assertEqual(self.new_contributor.id, field.contributor_id)

    @override_settings(
        BATCH_JOB_QUEUE_NAME='queue', BATCH_JOB_DEF_NAME='job-def')
    @patch(SUBMIT)
    def test_failed_submission_falls_back_to_inline(self, submit):
        submit.side_effect = RuntimeError('batch is down')

        self.source.contributor = self.new_contributor
        self.save_source(self.source)

        submit.assert_called_once()
        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )

    @override_settings(
        BATCH_JOB_QUEUE_NAME=None, BATCH_JOB_DEF_NAME=None)
    @patch(SUBMIT)
    def test_unconfigured_batch_reassigns_inline(self, submit):
        self.source.contributor = self.new_contributor
        self.save_source(self.source)

        submit.assert_not_called()
        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )


class ReassignExtendedFieldsBatchActionTest(SourceReassignmentTestBase):
    """
    The `reassign_extended_fields` batch_process action is what the
    Batch job submitted by SourceService.schedule_reassignment runs.
    """

    def test_action_reassigns_the_lists_source(self):
        # A queryset update bypasses Source.save(), creating the same
        # drift the Batch job is submitted to repair.
        Source.objects.filter(pk=self.source.pk).update(
            contributor=self.new_contributor)

        call_command(
            'batch_process',
            '--action', 'reassign_extended_fields',
            '--list-id', str(self.list.id),
        )

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.new_contributor.id,
            self.extended_field.contributor_id,
        )


class SourceAdminReassignmentMessageTest(SourceReassignmentTestBase):
    """
    The admin save returns before the re-attribution completes, so the
    change view must tell the admin the rest is coming. See OSDEV-3758.
    """

    class FakeForm:
        def __init__(self, changed_data):
            self.changed_data = changed_data

    def admin_request(self):
        request = RequestFactory().post('/admin/api/source/')
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request

    def save_model(self, changed_data):
        model_admin = SourceAdmin(Source, admin_site)
        request = self.admin_request()
        with self.captureOnCommitCallbacks(execute=True):
            model_admin.save_model(
                request,
                self.source,
                self.FakeForm(changed_data),
                change=True,
            )
        return [str(message) for message in get_messages(request)]

    def test_contributor_change_messages_the_admin(self):
        self.source.contributor = self.new_contributor
        sent = self.save_model(changed_data=['contributor'])

        self.assertEqual(1, len(sent))
        self.assertIn('scheduled', sent[0])

    def test_other_changes_do_not_message(self):
        self.source.is_active = False
        sent = self.save_model(changed_data=['is_active'])

        self.assertEqual([], sent)
