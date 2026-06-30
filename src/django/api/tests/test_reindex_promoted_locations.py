from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from api.constants import ProcessingAction
from api.models import Contributor, User
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source

INDEX_PATH = (
    'api.management.commands.reindex_promoted_locations.index_facilities_new'
)


class ReindexPromotedLocationsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _make_facility(self, os_id, promoted):
        source = Source.objects.create(
            contributor=self.contributor,
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
        )
        processing_results = (
            [{'action': ProcessingAction.PROMOTE_MATCH, 'error': False}]
            if promoted else []
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
            processing_results=processing_results,
        )
        return Facility.objects.create(
            id=os_id,
            name='Facility',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

    @patch(INDEX_PATH)
    def test_reindexes_only_promoted_locations(self, mock_index):
        self._make_facility('US2024000PROMO', promoted=True)
        self._make_facility('US2024000PLAIN', promoted=False)

        call_command('reindex_promoted_locations')

        self.assertTrue(mock_index.called)
        reindexed = [
            os_id
            for call in mock_index.call_args_list
            for os_id in call.args[0]
        ]
        self.assertIn('US2024000PROMO', reindexed)
        self.assertNotIn('US2024000PLAIN', reindexed)

    @patch(INDEX_PATH)
    def test_dry_run_does_not_reindex(self, mock_index):
        self._make_facility('US2024000PROMO', promoted=True)

        call_command('reindex_promoted_locations', '--dry-run')

        mock_index.assert_not_called()

    @patch(INDEX_PATH)
    def test_no_promoted_locations_skips_reindex(self, mock_index):
        self._make_facility('US2024000PLAIN', promoted=False)

        call_command('reindex_promoted_locations')

        mock_index.assert_not_called()

    @patch(INDEX_PATH)
    def test_respects_batch_size(self, mock_index):
        for i in range(3):
            self._make_facility(f'US202400PROMO{i}', promoted=True)

        call_command('reindex_promoted_locations', '--batch-size', '2')

        # 3 promoted locations with batch size 2 -> 2 batches.
        self.assertEqual(mock_index.call_count, 2)
        reindexed = [
            os_id
            for call in mock_index.call_args_list
            for os_id in call.args[0]
        ]
        self.assertEqual(len(reindexed), 3)
