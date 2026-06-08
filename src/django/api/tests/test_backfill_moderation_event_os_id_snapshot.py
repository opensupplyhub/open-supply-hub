from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from api.models import Contributor, ModerationEvent, User
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source


class BackfillModerationEventOsIdSnapshotTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.source = Source.objects.create(
            contributor=self.contributor,
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
        )
        self.list_item = FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.facility = Facility.objects.create(
            id='US2026000ABCDEF',
            name='Facility',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )

    def _make_event(self, status, os_id, os_id_snapshot):
        return ModerationEvent.objects.create(
            contributor=self.contributor,
            status=status,
            os_id=os_id,
            os_id_snapshot=os_id_snapshot,
            request_type='UPDATE',
            raw_data={},
            cleaned_data={},
        )

    def test_backfills_approved_event_with_empty_snapshot(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=self.facility.id,
            os_id_snapshot='',
        )

        call_command('backfill_moderation_event_os_id_snapshot')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, self.facility.id)

    def test_does_not_overwrite_existing_snapshot(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=self.facility.id,
            os_id_snapshot='US2020000PREEXIST',
        )

        call_command('backfill_moderation_event_os_id_snapshot')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, 'US2020000PREEXIST')

    def test_does_not_backfill_approved_events_with_null_os_id(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )

        call_command('backfill_moderation_event_os_id_snapshot')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')

    def test_does_not_backfill_non_approved_events(self):
        event = self._make_event(
            status=ModerationEvent.Status.PENDING,
            os_id=self.facility.id,
            os_id_snapshot='',
        )

        call_command('backfill_moderation_event_os_id_snapshot')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')

    def test_dry_run_does_not_write(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=self.facility.id,
            os_id_snapshot='',
        )

        call_command('backfill_moderation_event_os_id_snapshot', '--dry-run')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')
