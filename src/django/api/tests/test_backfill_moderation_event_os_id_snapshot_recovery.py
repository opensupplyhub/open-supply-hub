from unittest.mock import MagicMock, patch

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase
from opensearchpy.exceptions import (
    ConnectionError as OpenSearchConnectionError,
)

from api.models import Contributor, ModerationEvent, User
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source

PATCH_TARGET = (
    'api.management.commands.'
    'backfill_moderation_event_os_id_snapshot_recovery.'
    'OpenSearchServiceConnection'
)


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

    def _opensearch_hits(self, items):
        return {
            'hits': {
                'hits': [
                    {'_source': {'moderation_id': mid, 'os_id': oid}}
                    for mid, oid in items
                ]
            }
        }

    @patch(PATCH_TARGET)
    def test_recovers_os_id_from_opensearch(self, mock_conn_class):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )

        mock_conn = MagicMock()
        mock_conn.client.search.return_value = self._opensearch_hits(
            [(str(event.uuid), 'US2020000RECOVER')]
        )
        mock_conn_class.return_value = mock_conn

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, 'US2020000RECOVER')
        self.assertIsNone(event.os_id)

    @patch(PATCH_TARGET)
    def test_falls_back_to_facility_list_item_when_opensearch_misses(
        self, mock_conn_class
    ):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )
        self._make_facility_with_list_item(
            os_id='US2020000FALLBCK', event=event
        )

        mock_conn = MagicMock()
        mock_conn.client.search.return_value = self._opensearch_hits([])
        mock_conn_class.return_value = mock_conn

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, 'US2020000FALLBCK')

    @patch(PATCH_TARGET)
    def test_dry_run_does_not_write(self, mock_conn_class):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )

        mock_conn = MagicMock()
        mock_conn.client.search.return_value = self._opensearch_hits(
            [(str(event.uuid), 'US2020000RECOVER')]
        )
        mock_conn_class.return_value = mock_conn

        call_command(
            'backfill_moderation_event_os_id_snapshot_recovery',
            '--dry-run',
        )

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')

    @patch(PATCH_TARGET)
    def test_opensearch_error_does_not_crash_and_uses_fallback(
        self, mock_conn_class
    ):
        event = self._make_event(
            status=ModerationEvent.Status.APPROVED,
            os_id=None,
            os_id_snapshot='',
        )
        self._make_facility_with_list_item(
            os_id='US2020000FALLBCK', event=event
        )

        mock_conn = MagicMock()
        mock_conn.client.search.side_effect = OpenSearchConnectionError(
            'N/A', 'connection refused', None
        )
        mock_conn_class.return_value = mock_conn

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, 'US2020000FALLBCK')

    @patch(PATCH_TARGET)
    def test_does_not_touch_pending_events(self, mock_conn_class):
        event = self._make_event(
            status=ModerationEvent.Status.PENDING,
            os_id=None,
            os_id_snapshot='',
        )

        mock_conn = MagicMock()
        mock_conn.client.search.return_value = self._opensearch_hits(
            [(str(event.uuid), 'US2020000IGNORED')]
        )
        mock_conn_class.return_value = mock_conn

        call_command('backfill_moderation_event_os_id_snapshot_recovery')

        event.refresh_from_db()
        self.assertEqual(event.os_id_snapshot, '')
