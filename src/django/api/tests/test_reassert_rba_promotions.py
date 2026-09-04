from api.constants import OriginSource, ProcessingAction
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.reassert_rba_promotions import (
    find_reverted_promotions,
    reassert_rba_promotions,
)

from django.contrib.gis.geos import Point
from django.test import TestCase


class ReassertRbaPromotionsTest(TestCase):
    '''
    The sync from OS Hub overwrites shared facilities, including
    created_from, which reverts promotions made on the RBA instance. These
    tests cover the query that finds those reverted promotions and the
    re-assertion that restores them.
    '''

    def setUp(self):
        self.user = User.objects.create(email='one@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='list 1'
        )
        self.source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.facility_list,
            contributor=self.contributor,
        )

        self.public_item = self.create_item(
            name='Public Name',
            address='Public Address',
            origin_source=OriginSource.OSHUB,
        )
        self.facility = Facility.objects.create(
            id='US2021250D1DTNT',
            name=self.public_item.name,
            address=self.public_item.address,
            country_code='US',
            location=Point(0, 0),
            created_from=self.public_item,
            origin_source=OriginSource.OSHUB,
        )
        self.public_item.facility = self.facility
        self.public_item.save()

    def create_item(self, name, address, origin_source,
                    status=FacilityListItem.CONFIRMED_MATCH):
        return FacilityListItem.objects.create(
            row_index=FacilityListItem.objects.count(),
            source=self.source,
            sector=[],
            status=status,
            name=name,
            address=address,
            country_code='US',
            geocoded_point=Point(1, 1),
            processing_results=[],
            origin_source=origin_source,
        )

    def create_match(self, item, origin_source=OriginSource.RBA,
                     status=FacilityMatch.CONFIRMED, is_active=True):
        return FacilityMatch.objects.create(
            facility_list_item=item,
            facility=self.facility,
            results={},
            confidence=1.0,
            status=status,
            is_active=is_active,
            origin_source=origin_source,
        )

    def create_rba_contribution(self, name='RBA Name',
                                address='RBA Address', **kwargs):
        item = self.create_item(
            name=name,
            address=address,
            origin_source=OriginSource.RBA,
            status=kwargs.pop('item_status',
                              FacilityListItem.CONFIRMED_MATCH),
        )
        return item, self.create_match(item, **kwargs)

    def test_restores_a_reverted_promotion(self):
        item, match = self.create_rba_contribution()

        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['found'])
        self.assertEqual(1, summary['reasserted'])
        self.assertEqual(0, summary['errors'])

        self.facility.refresh_from_db()
        self.assertEqual(item.id, self.facility.created_from_id)
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual('RBA Address', self.facility.address)

    def test_records_the_promotion_on_the_list_item(self):
        item, _ = self.create_rba_contribution()

        reassert_rba_promotions()

        item.refresh_from_db()
        self.assertEqual(1, len(item.processing_results))
        result = item.processing_results[0]
        self.assertEqual(ProcessingAction.PROMOTE_MATCH, result['action'])
        self.assertFalse(result['error'])
        self.assertEqual(
            self.public_item.id, result['previous_created_from_id']
        )

    def test_change_reason_stays_parseable_by_facility_history(self):
        # facility_history matches on the substring 'Promoted' to render a
        # promotion as an update with a location diff.
        self.create_rba_contribution()

        reassert_rba_promotions()

        self.facility.refresh_from_db()
        reason = self.facility.history.first().history_change_reason
        self.assertIn('Promoted', reason)
        self.assertIn('re-asserted after sync', reason)

    def simulate_sync_overwrite(self):
        '''
        Apply the mutation the daily sync applies to a shared facility.

        sync_databases copies every synced field from the public row onto
        the RBA row and re-points created_from at the public list item.
        This reproduces that write rather than running the sync itself,
        which needs a second database to read from.
        '''
        self.facility.name = self.public_item.name
        self.facility.address = self.public_item.address
        self.facility.country_code = self.public_item.country_code
        self.facility.created_from = self.public_item
        self.facility.save()

    def test_contribution_survives_a_sync_overwrite(self):
        # The whole design rests on the contribution outliving the
        # overwrite: the sync only upserts rows that also exist publicly,
        # and an RBA list item and match do not.
        item, match = self.create_rba_contribution()
        reassert_rba_promotions()

        self.simulate_sync_overwrite()

        item.refresh_from_db()
        match.refresh_from_db()
        self.assertEqual('RBA Name', item.name)
        self.assertEqual('RBA Address', item.address)
        self.assertEqual(FacilityListItem.CONFIRMED_MATCH, item.status)
        self.assertEqual(OriginSource.RBA, item.origin_source)
        self.assertEqual(FacilityMatch.CONFIRMED, match.status)
        self.assertTrue(match.is_active)
        self.assertEqual(OriginSource.RBA, match.origin_source)

    def test_restores_the_promotion_after_a_sync_overwrite(self):
        item, _ = self.create_rba_contribution()
        reassert_rba_promotions()

        self.simulate_sync_overwrite()

        # The facility now shows the public values again.
        self.facility.refresh_from_db()
        self.assertEqual('Public Name', self.facility.name)
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

        # The reverted promotion is detected and restored, and the values
        # come from the surviving list item.
        self.assertEqual(1, find_reverted_promotions().count())
        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['reasserted'])
        self.facility.refresh_from_db()
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual('RBA Address', self.facility.address)
        self.assertEqual(item.id, self.facility.created_from_id)

    def test_survives_repeated_sync_overwrites(self):
        item, _ = self.create_rba_contribution()

        for _ in range(3):
            self.simulate_sync_overwrite()
            reassert_rba_promotions()

        self.facility.refresh_from_db()
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual(item.id, self.facility.created_from_id)

        # Each cycle records one promotion; nothing is duplicated or lost.
        item.refresh_from_db()
        self.assertEqual(3, len(item.processing_results))

    def test_is_a_no_op_once_the_promotion_is_in_place(self):
        self.create_rba_contribution()

        reassert_rba_promotions()
        second_run = reassert_rba_promotions()

        self.assertEqual(0, second_run['found'])
        self.assertEqual(0, second_run['reasserted'])

    def test_promotes_the_newest_rba_contribution(self):
        self.create_rba_contribution(name='Older', address='Older Address')
        newer_item, _ = self.create_rba_contribution(
            name='Newer', address='Newer Address'
        )

        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(newer_item.id, self.facility.created_from_id)
        self.assertEqual('Newer', self.facility.name)

    def test_never_demotes_to_an_older_contribution(self):
        # With the newest contribution already promoted, the older one must
        # not be selected - otherwise every run would flip the facility back.
        self.create_rba_contribution(name='Older', address='Older Address')
        newer_item, _ = self.create_rba_contribution(
            name='Newer', address='Newer Address'
        )
        self.facility.created_from = newer_item
        self.facility.name = newer_item.name
        self.facility.save()

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(newer_item.id, self.facility.created_from_id)

    def test_ignores_contributions_that_did_not_originate_here(self):
        item = self.create_item(
            name='Other Contributor',
            address='Other Address',
            origin_source=OriginSource.OSHUB,
        )
        self.create_match(item, origin_source=OriginSource.OSHUB)

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

    def test_ignores_inactive_matches(self):
        self.create_rba_contribution(is_active=False)

        self.assertEqual(0, find_reverted_promotions().count())

    def test_ignores_unconfirmed_matches(self):
        self.create_rba_contribution(status=FacilityMatch.PENDING)

        self.assertEqual(0, find_reverted_promotions().count())

    def test_ignores_items_that_are_not_matched(self):
        self.create_rba_contribution(
            item_status=FacilityListItem.POTENTIAL_MATCH
        )

        self.assertEqual(0, find_reverted_promotions().count())

    def test_dry_run_reports_without_changing_anything(self):
        self.create_rba_contribution()

        summary = reassert_rba_promotions(dry_run=True)

        self.assertEqual(1, summary['found'])
        self.assertEqual(0, summary['reasserted'])
        self.assertTrue(summary['dry_run'])

        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)
        self.assertEqual('Public Name', self.facility.name)

    def test_limit_caps_the_number_processed(self):
        other_item = self.create_item(
            name='Second Public',
            address='Second Public Address',
            origin_source=OriginSource.OSHUB,
        )
        other_facility = Facility.objects.create(
            id='US2021250D1DTNU',
            name=other_item.name,
            address=other_item.address,
            country_code='US',
            location=Point(0, 0),
            created_from=other_item,
            origin_source=OriginSource.OSHUB,
        )
        other_item.facility = other_facility
        other_item.save()

        self.create_rba_contribution()
        rba_item = self.create_item(
            name='Second RBA',
            address='Second RBA Address',
            origin_source=OriginSource.RBA,
        )
        FacilityMatch.objects.create(
            facility_list_item=rba_item,
            facility=other_facility,
            results={},
            confidence=1.0,
            status=FacilityMatch.CONFIRMED,
            is_active=True,
            origin_source=OriginSource.RBA,
        )

        self.assertEqual(2, find_reverted_promotions().count())

        summary = reassert_rba_promotions(limit=1)

        self.assertEqual(1, summary['found'])
        self.assertEqual(1, summary['reasserted'])
