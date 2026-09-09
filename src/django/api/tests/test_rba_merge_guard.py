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
    On the RBA private instance, merging a record that also exists on public
    OS Hub produces state the one-way sync cannot repair - it recreates the
    merged-away facility on the next run. These tests cover the guard that
    refuses those merges, and confirm public OS Hub is unaffected.
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
        # origin_source is stamped by a trigger/signal from the running
        # instance's own setting, so set it explicitly to model a record
        # that arrived from elsewhere.
        Facility.objects.filter(id=os_id).update(origin_source=origin_source)
        facility.refresh_from_db()

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

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_allows_merging_two_records_created_on_this_instance(self):
        response = self.post_merge()

        self.assertEqual(200, response.status_code)
        self.assertFalse(Facility.objects.filter(id=self.merge.id).exists())

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_refuses_when_the_merged_record_is_publicly_synced(self):
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn(self.merge.id, str(response.data))

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_refuses_when_the_target_record_is_publicly_synced(self):
        self.set_origin(self.target, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn(self.target.id, str(response.data))

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_names_both_records_when_neither_is_mergeable(self):
        self.set_origin(self.target, OriginSource.OSHUB)
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(400, response.status_code)
        self.assertIn(self.target.id, str(response.data))
        self.assertIn(self.merge.id, str(response.data))

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    def test_refuses_an_unstamped_record(self):
        # origin_source is nullable and the trigger's fallback is os_hub, so
        # an unstamped record must not be assumed local. Fail closed.
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

    @override_settings(INSTANCE_SOURCE=OriginSource.OSHUB)
    def test_public_os_hub_is_unaffected(self):
        # The guard is instance-scoped: on public OS Hub a moderator merges
        # exactly as before, including records this instance did not create.
        self.set_origin(self.target, OriginSource.OSHUB)
        self.set_origin(self.merge, OriginSource.OSHUB)

        response = self.post_merge()

        self.assertEqual(200, response.status_code)
        self.assertFalse(Facility.objects.filter(id=self.merge.id).exists())
