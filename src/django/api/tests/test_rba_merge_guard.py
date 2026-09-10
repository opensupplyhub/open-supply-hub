from api.constants import OriginSource
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.signals import location_post_delete_handler_for_opensearch

from django.contrib.gis.geos import Point
from django.db.models.signals import post_delete
from django.test import override_settings
from rest_framework.test import APITestCase


class RbaMergeGuardTest(APITestCase):
    '''
    On the RBA private instance, merging AWAY a record that also exists on
    public OS Hub produces state the one-way sync cannot repair - it
    recreates that record on the next run. These tests cover the guard that
    refuses those merges, confirm that a publicly-synced *target* is still
    mergeable into (the ordinary cleanup case), and confirm public OS Hub is
    unaffected.
    '''

    def setUp(self):
        # Location deletion propagation to OpenSearch is out of scope for
        # Django unit tests.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch,
            Facility
        )

        self.superuser_email = 'super@example.com'
        self.superuser_password = 'example123'
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor = Contributor.objects.create(
            admin=self.superuser,
            name='contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='list 1'
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.target = self.create_facility('US2021250D1DTNT')
        self.merge = self.create_facility('US2021250D1DTNU')

        self.merge_url = '/api/facilities/merge/?target={}&merge={}'.format(
            self.target.id, self.merge.id
        )

    def create_facility(self, os_id, origin_source=OriginSource.RBA):
        item = FacilityListItem.objects.create(
            name='Name',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=FacilityListItem.objects.count(),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        facility = Facility.objects.create(
            id=os_id,
            name='Name',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=item,
        )
        # origin_source is stamped from the running instance's own setting,
        # so set it explicitly to model a record that arrived from elsewhere.
        self.set_origin(facility, origin_source)

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=item,
            confidence=0.85,
            results='',
        )
        item.facility = facility
        item.save()
        return facility

    def set_origin(self, facility, origin_source):
        Facility.objects.filter(id=facility.id).update(
            origin_source=origin_source
        )
        facility.refresh_from_db()

    def post_merge(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        return self.client.post(self.merge_url)

    def assert_merge_succeeded(self, response):
        self.assertEqual(200, response.status_code)
        self.assertFalse(Facility.objects.filter(id=self.merge.id).exists())

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_allows_merging_two_records_created_on_this_instance(self):
        self.assert_merge_succeeded(self.post_merge())

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_allows_merging_a_local_record_into_a_publicly_synced_one(self):
        # The ordinary cleanup case: a duplicate created here is absorbed
        # into the synced record it duplicates. Only the merged-away record
        # can be recreated by the sync, and that one is local, so the merge
        # is durable. The merge writes none of the target's synced fields,
        # so the synced target is untouched by it.
        self.set_origin(self.target, OriginSource.OSHUB)

        self.assert_merge_succeeded(self.post_merge())

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_refuses_merging_away_a_publicly_synced_record(self):
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn(self.merge.id, str(response.data))

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_refuses_merging_away_an_unstamped_record(self):
        # origin_source is nullable and an unstamped row stays NULL, so a
        # record we cannot prove is local must not be assumed local.
        self.set_origin(self.merge, None)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn(self.merge.id, str(response.data))

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_a_refused_merge_writes_nothing(self):
        self.set_origin(self.merge, OriginSource.OSHUB)
        facility_count = Facility.objects.count()
        match = FacilityMatch.objects.get(facility=self.merge)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertEqual(facility_count, Facility.objects.count())
        match.refresh_from_db()
        self.assertEqual(self.merge.id, match.facility_id)
        self.assertEqual(FacilityMatch.AUTOMATIC, match.status)

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_the_error_explains_the_alternative(self):
        # The admin cannot always act on "merge it on OS Hub instead" - the
        # local duplicate does not exist there - so the message has to point
        # at merging the other direction.
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        detail = str(response.data)
        self.assertIn('created here', detail)
        self.assertIn('instead', detail)

    @override_settings(INSTANCE_SOURCE=OriginSource.OSHUB)
    def test_public_os_hub_is_unaffected(self):
        # The guard is instance-scoped: on public OS Hub a moderator merges
        # exactly as before, including records this instance did not create.
        self.set_origin(self.target, OriginSource.OSHUB)
        self.set_origin(self.merge, OriginSource.OSHUB)

        self.assert_merge_succeeded(self.post_merge())

    @override_settings(INSTANCE_SOURCE='  RBA  ')
    def test_the_instance_value_is_normalized(self):
        # The value comes from an environment variable in a task
        # definition. Stray casing or whitespace must not silently disable
        # the guard, which would be invisible until unrepairable state
        # appeared.
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)

    @override_settings(INSTANCE_SOURCE='not-a-real-source')
    def test_an_unrecognized_instance_value_refuses_the_merge(self):
        # An unrecognized value must not resolve to os_hub. That is the
        # value that makes is_rba_instance() false, so a task-definition
        # typo on this instance would silently disarm the guard - the one
        # failure mode with no trace and unrepairable consequences.
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn('misconfigured', str(response.data))

    @override_settings(INSTANCE_SOURCE='not-a-real-source')
    def test_an_unrecognized_instance_value_fails_closed_for_any_record(
        self
    ):
        # Fails closed on the origin check too: when we cannot identify the
        # deployment we cannot evaluate whether the merge is safe, so being
        # locally stamped does not earn an exemption. A refused merge is
        # loud and immediately recoverable; a half-applied one is not.
        self.set_origin(self.merge, OriginSource.RBA)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertTrue(Facility.objects.filter(id=self.merge.id).exists())

    @override_settings(INSTANCE_SOURCE='')
    def test_an_unset_instance_value_is_public_os_hub(self):
        # Unset is not a misconfiguration - it is what every environment
        # other than a private instance looks like, so it must keep
        # behaving as public OS Hub rather than refusing merges.
        self.set_origin(self.merge, OriginSource.OSHUB)

        self.assert_merge_succeeded(self.post_merge())
