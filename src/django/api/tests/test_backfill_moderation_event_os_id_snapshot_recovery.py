from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from api.models import Contributor, ModerationEvent, User
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source


class BackfillModerationEventOsIdSnapshotRecoveryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
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

    def _make_facility_with_list_item(self, os_id, event=None):
        source = Source.objects.create(
            contributor=self.contributor,
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
        )
        list_item = FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
            facility_id=os_id,
            moderation_event=event,
        )
        return Facility.objects.create(
            id=os_id,
            name='Facility',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

    def test_recovers_os_id_from_facility_list_item(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )
        self._make_facility_with_list_item(
            os_id='US2020000RECOVER', event=event
        )

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, 'US2020000RECOVER')
        self.assertIsNone(event.os_id)

    def test_unrecoverable_without_linked_list_item(self):
        # No FacilityListItem links to this event, so there's nothing to
        # recover from — the snapshot stays empty.
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')

    def test_dry_run_does_not_write(self):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )
        self._make_facility_with_list_item(
            os_id='US2020000RECOVER', event=event
        )

        call_command(
            'backfill_moderation_event_os_id_snapshot_recovery',
            '--dry-run',
        )

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')

    def test_does_not_touch_pending_events(self):
        event = self._make_event(
            status=ModerationEvent.Status.PENDING,
            os_id=None,
            os_id_snapshot='',
        )
        self._make_facility_with_list_item(
            os_id='US2020000IGNORED', event=event
        )

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')
