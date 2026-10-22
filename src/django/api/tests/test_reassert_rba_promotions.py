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
    PromotionConflict,
    find_reverted_promotions,
    reassert_promotion,
    reassert_rba_promotions,
)

from django.contrib.gis.geos import Point
from django.test import TestCase


class ReassertRbaPromotionsTest(TestCase):
    '''
    The sync from OS Hub overwrites shared facilities, including
    created_from, which reverts promotions made on the RBA instance.

    What counts as a promotion is read from the facility's own history,
    not from a PROMOTE_MATCH processing result on the item: the facility
    delete flow appends that marker to every other matched item, so it
    does not identify the promoted one, and only history orders a
    promotion against everything else that happened to the facility.
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
                    status=FacilityListItem.CONFIRMED_MATCH,
                    geocoded_point=Point(1, 1)):
        return FacilityListItem.objects.create(
            row_index=FacilityListItem.objects.count(),
            source=self.source,
            sector=[],
            status=status,
            name=name,
            address=address,
            country_code='US',
            geocoded_point=geocoded_point,
            processing_results=[],
            origin_source=origin_source,
        )

    def create_match(self, item, origin_source=OriginSource.RBA,
                     status=FacilityMatch.CONFIRMED, is_active=True,
                     facility=None):
        return FacilityMatch.objects.create(
            facility_list_item=item,
            facility=facility or self.facility,
            results={},
            confidence=1.0,
            status=status,
            is_active=is_active,
            origin_source=origin_source,
        )

    def promote(self, item):
        '''
        Promote as the endpoint does, so the facility's history records it.

        The endpoint sets the canonical fields and created_from with a
        'Promoted ... over ...' change reason; that reason is what marks a
        deliberate promotion.
        '''
        previous = self.facility.created_from
        self.facility.name = item.name
        self.facility.address = item.address
        self.facility.country_code = item.country_code
        self.facility.location = item.geocoded_point
        self.facility.created_from = item
        self.facility._change_reason = (
            f'Promoted item {item.id} over item {previous.id}'
        )
        self.facility.save()
        # simple_history reads _change_reason off the instance, so clear it
        # or the next save on this same object inherits the reason and
        # looks like another promotion.
        self.facility._change_reason = None
        return item

    def create_rba_contribution(self, name='RBA Name',
                                address='RBA Address', promoted=True,
                                geocoded_point=Point(1, 1), **kwargs):
        item = self.create_item(
            name=name,
            address=address,
            origin_source=OriginSource.RBA,
            status=kwargs.pop('item_status',
                              FacilityListItem.CONFIRMED_MATCH),
            geocoded_point=geocoded_point,
        )
        match = self.create_match(item, **kwargs)
        if promoted:
            self.promote(item)
        return item, match

    def simulate_sync_overwrite(self):
        '''
        Apply the mutation the daily sync applies to a shared facility.

        sync_databases copies every synced field from the public row onto
        the RBA row and re-points created_from at the public list item.
        Note it carries no 'Promoted' change reason, which is what makes
        the reverted state distinguishable from a moderator's decision.
        '''
        self.facility.name = self.public_item.name
        self.facility.address = self.public_item.address
        self.facility.country_code = self.public_item.country_code
        self.facility.created_from = self.public_item
        self.facility._change_reason = None
        self.facility.save()

    def test_restores_a_promotion_reverted_by_the_sync(self):
        item, _ = self.create_rba_contribution()

        self.simulate_sync_overwrite()
        self.facility.refresh_from_db()
        self.assertEqual('Public Name', self.facility.name)

        self.assertEqual(1, len(find_reverted_promotions()))
        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['reasserted'])
        self.assertEqual(0, summary['errors'])
        self.facility.refresh_from_db()
        self.assertEqual(item.id, self.facility.created_from_id)
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual('RBA Address', self.facility.address)

    def test_is_a_no_op_while_the_promotion_is_in_force(self):
        self.create_rba_contribution()

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.assertEqual(0, summary['reasserted'])

    def test_ignores_a_contribution_that_was_never_promoted(self):
        # The ordinary outcome of an RBA contribution: matched to an
        # existing facility, never promoted.
        self.create_rba_contribution(promoted=False)

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

    def test_ignores_a_promote_match_marker_on_an_unpromoted_item(self):
        # The facility delete flow appends PROMOTE_MATCH to every other
        # matched item, so the marker does not mean this item was
        # promoted. Selection must not rely on it.
        item, _ = self.create_rba_contribution(promoted=False)
        item.processing_results.append({
            'action': ProcessingAction.PROMOTE_MATCH,
            'started_at': '2026-01-01 00:00:00+00:00',
            'error': False,
            'finished_at': '2026-01-01 00:00:00+00:00',
            'promoted_os_id': self.facility.id,
        })
        item.save()

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

    def test_respects_a_later_promotion_of_a_public_contribution(self):
        # Promoting a public contribution is how a moderator undoes an RBA
        # promotion. That decision is the most recent one, so it stands.
        self.create_rba_contribution()
        self.promote(self.public_item)

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

    def test_restores_the_newest_promotion_not_the_newest_contribution(self):
        # Two RBA contributions, but the moderator's last promotion was the
        # older one. That is what gets restored.
        older_item, _ = self.create_rba_contribution(
            name='Older', address='Older Address'
        )
        self.create_rba_contribution(
            name='Newer', address='Newer Address', promoted=False
        )
        self.promote(older_item)

        self.simulate_sync_overwrite()
        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['reasserted'])
        self.facility.refresh_from_db()
        self.assertEqual(older_item.id, self.facility.created_from_id)
        self.assertEqual('Older', self.facility.name)

    def test_promotes_the_most_recently_promoted_of_several(self):
        self.create_rba_contribution(name='Older', address='Older Address')
        newer_item, _ = self.create_rba_contribution(
            name='Newer', address='Newer Address'
        )

        self.simulate_sync_overwrite()
        summary = reassert_rba_promotions()

        self.assertEqual(1, summary['reasserted'])
        self.facility.refresh_from_db()
        self.assertEqual(newer_item.id, self.facility.created_from_id)
        self.assertEqual('Newer', self.facility.name)

    def test_records_the_re_assertion_on_the_list_item(self):
        item, _ = self.create_rba_contribution()
        self.simulate_sync_overwrite()

        reassert_rba_promotions()

        item.refresh_from_db()
        result = item.processing_results[-1]
        self.assertEqual(ProcessingAction.PROMOTE_MATCH, result['action'])
        self.assertFalse(result['error'])
        self.assertEqual(
            self.public_item.id, result['previous_created_from_id']
        )

    def test_change_reason_stays_parseable_by_facility_history(self):
        # facility_history matches on the substring 'Promoted' to render a
        # promotion, and the prefix also makes the re-assertion itself the
        # facility's latest promotion.
        self.create_rba_contribution()
        self.simulate_sync_overwrite()

        reassert_rba_promotions()

        self.facility.refresh_from_db()
        reason = self.facility.history.first().history_change_reason
        self.assertTrue(reason.startswith('Promoted '))
        self.assertIn('re-asserted after sync', reason)

    def test_contribution_survives_a_sync_overwrite(self):
        # The whole design rests on the contribution outliving the
        # overwrite: the sync only upserts rows that also exist publicly,
        # and an RBA list item and match do not.
        item, match = self.create_rba_contribution()

        self.simulate_sync_overwrite()

        item.refresh_from_db()
        match.refresh_from_db()
        self.assertEqual('RBA Name', item.name)
        self.assertEqual(FacilityListItem.CONFIRMED_MATCH, item.status)
        self.assertEqual(OriginSource.RBA, item.origin_source)
        self.assertEqual(FacilityMatch.CONFIRMED, match.status)
        self.assertTrue(match.is_active)
        self.assertEqual(OriginSource.RBA, match.origin_source)

    def test_survives_repeated_sync_overwrites(self):
        item, _ = self.create_rba_contribution()

        for _ in range(3):
            self.simulate_sync_overwrite()
            reassert_rba_promotions()

        self.facility.refresh_from_db()
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual(item.id, self.facility.created_from_id)

    def test_does_not_revert_a_concurrent_change_to_another_field(self):
        # The facility is saved with update_fields, so a value written
        # after the reverted set was built is not clobbered from a stale
        # in-memory copy.
        self.create_rba_contribution()
        self.simulate_sync_overwrite()
        matches = find_reverted_promotions()

        Facility.objects.filter(id=self.facility.id).update(is_closed=True)

        reassert_rba_promotions()

        self.facility.refresh_from_db()
        self.assertTrue(self.facility.is_closed)
        self.assertEqual('RBA Name', self.facility.name)
        self.assertEqual(1, len(matches))

    def test_does_not_clobber_a_concurrent_processing_result(self):
        # Appending to processing_results is a read-modify-write, while
        # aws_batch appends with raw SQL across every item of a source. The
        # item is therefore locked and re-read inside the transaction: a
        # result written after the set was built must survive, rather than
        # being overwritten from the stale in-memory list the match carries.
        item, _ = self.create_rba_contribution()
        self.simulate_sync_overwrite()
        matches = find_reverted_promotions()

        concurrent = list(
            FacilityListItem.objects.get(id=item.id).processing_results
        )
        concurrent.append({'action': ProcessingAction.PARSE, 'error': False})
        FacilityListItem.objects.filter(id=item.id).update(
            processing_results=concurrent
        )

        reassert_promotion(matches[0])

        item.refresh_from_db()
        actions = [
            result['action'] for result in item.processing_results
        ]
        self.assertIn(ProcessingAction.PARSE, actions)
        self.assertEqual(ProcessingAction.PROMOTE_MATCH, actions[-1])

    def test_reports_an_item_that_lost_its_geocode_before_the_write(self):
        # The selection query excludes ungeocoded items, so this can only
        # happen between selection and the write. Facility.location is not
        # nullable, so the save would raise IntegrityError and be swallowed
        # as a generic error.
        item, _ = self.create_rba_contribution()
        self.simulate_sync_overwrite()
        matches = find_reverted_promotions()

        FacilityListItem.objects.filter(id=item.id).update(
            geocoded_point=None
        )

        with self.assertRaises(PromotionConflict) as caught:
            reassert_promotion(matches[0])

        self.assertIn('geocoded point', str(caught.exception))
        self.facility.refresh_from_db()
        self.assertEqual(self.public_item.id, self.facility.created_from_id)

    def test_reports_a_created_from_conflict_distinctly(self):
        # created_from is a OneToOneField. If the item became another
        # facility's created_from, saving would raise IntegrityError and be
        # swallowed as a generic failure.
        item, match = self.create_rba_contribution()
        self.simulate_sync_overwrite()

        other_item = self.create_item(
            name='Other', address='Other Address',
            origin_source=OriginSource.OSHUB,
        )
        other_facility = Facility.objects.create(
            id='US2021250D1DTNU',
            name='Other',
            address='Other Address',
            country_code='US',
            location=Point(0, 0),
            created_from=other_item,
            origin_source=OriginSource.OSHUB,
        )
        Facility.objects.filter(id=other_facility.id).update(
            created_from_id=item.id
        )

        with self.assertRaises(PromotionConflict):
            from api.reassert_rba_promotions import reassert_promotion
            reassert_promotion(match)

        summary = reassert_rba_promotions()
        self.assertEqual(1, summary['errors'])
        self.assertEqual(0, summary['reasserted'])

    def test_ignores_contributions_that_did_not_originate_here(self):
        item = self.create_item(
            name='Other Contributor',
            address='Other Address',
            origin_source=OriginSource.OSHUB,
        )
        self.create_match(item, origin_source=OriginSource.OSHUB)
        self.promote(item)
        self.simulate_sync_overwrite()

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])

    def test_ignores_inactive_matches(self):
        self.create_rba_contribution(is_active=False)
        self.simulate_sync_overwrite()

        self.assertEqual(0, len(find_reverted_promotions()))

    def test_ignores_unconfirmed_matches(self):
        self.create_rba_contribution(status=FacilityMatch.PENDING)
        self.simulate_sync_overwrite()

        self.assertEqual(0, len(find_reverted_promotions()))

    def test_ignores_items_that_are_not_matched(self):
        self.create_rba_contribution(
            item_status=FacilityListItem.POTENTIAL_MATCH
        )
        self.simulate_sync_overwrite()

        self.assertEqual(0, len(find_reverted_promotions()))

    def test_ignores_a_promoted_item_with_no_geocoded_point(self):
        # geocoded_point is nullable on the item but Facility.location is
        # not, so selecting such a row would raise IntegrityError on save.
        # The promote endpoint excludes null points, so reach this state by
        # clearing the point after the promotion rather than before it.
        item, _ = self.create_rba_contribution()
        self.simulate_sync_overwrite()
        FacilityListItem.objects.filter(id=item.id).update(
            geocoded_point=None
        )

        summary = reassert_rba_promotions()

        self.assertEqual(0, summary['found'])
        self.assertEqual(0, summary['errors'])

    def test_dry_run_reports_without_changing_anything(self):
        self.create_rba_contribution()
        self.simulate_sync_overwrite()

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
        self.simulate_sync_overwrite()

        rba_item = self.create_item(
            name='Second RBA',
            address='Second RBA Address',
            origin_source=OriginSource.RBA,
        )
        self.create_match(rba_item, facility=other_facility)
        other_facility.created_from = rba_item
        other_facility._change_reason = (
            f'Promoted item {rba_item.id} over item {other_item.id}'
        )
        other_facility.save()
        Facility.objects.filter(id=other_facility.id).update(
            created_from_id=other_item.id
        )

        self.assertEqual(2, len(find_reverted_promotions()))

        summary = reassert_rba_promotions(limit=1)

        self.assertEqual(1, summary['found'])
        self.assertEqual(1, summary['reasserted'])

    def test_a_limit_below_one_is_rejected(self):
        for invalid in (0, -1):
            with self.assertRaises(ValueError):
                reassert_rba_promotions(limit=invalid)
