from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.transactions.index_facilities_new import index_facilities_new
from api.signals import location_post_delete_handler_for_opensearch
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models.signals import post_delete
from django.test import TestCase, override_settings

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'


class CandidateIndexExclusionTest(TestCase):
    """
    api_facilityindex never contains candidate facilities (OSDEV-3243).

    The index is written only by the index_facilities_by / index_facilities
    SQL procedures (0246), which the api_facility triggers call on every
    INSERT, UPDATE and DELETE. The test database runs the migrations, so
    these tests exercise the real triggers, not a Python re-implementation.
    """

    def setUp(self):
        # Disconnect location deletion propagation to OpenSearch cluster, as
        # it is outside the scope of Django unit testing.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch,
            Facility
        )
        self.addCleanup(
            post_delete.connect,
            location_post_delete_handler_for_opensearch,
            Facility
        )

        self.user = User.objects.create(email='one@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)
        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

    def _create_list_item(self):
        self.next_row_index += 1
        return FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

    def _create_facility(self, **kwargs):
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': self._create_list_item(),
        }
        defaults.update(kwargs)
        # Manager.create() does not apply the manager's filter, so this
        # works both before and after Facility.objects starts excluding
        # candidates (OSDEV-3380).
        return Facility.objects.create(**defaults)

    def _create_candidate(self, **kwargs):
        defaults = {
            'name': '',
            'address': '',
            'is_candidate': True,
            'polygon': GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            'confidence': 0.87,
            'external_id': 'eg-facility-0001',
            'source': 'earth_genome',
        }
        defaults.update(kwargs)
        return self._create_facility(**defaults)

    @staticmethod
    def _indexed(facility):
        return FacilityIndex.objects.filter(id=facility.id).exists()

    def test_creating_a_confirmed_facility_indexes_it(self):
        facility = self._create_facility()

        self.assertTrue(self._indexed(facility))

    def test_creating_a_candidate_does_not_index_it(self):
        candidate = self._create_candidate()

        self.assertFalse(self._indexed(candidate))

    def test_graduating_a_candidate_indexes_it(self):
        candidate = self._create_candidate()
        self.assertFalse(self._indexed(candidate))

        candidate.is_candidate = False
        candidate.name = 'Graduated'
        candidate.address = 'Address'
        candidate.save()

        self.assertTrue(self._indexed(candidate))
        self.assertEqual(
            FacilityIndex.objects.get(id=candidate.id).name, 'Graduated'
        )

    def test_reverting_a_facility_to_candidate_removes_it(self):
        facility = self._create_facility()
        self.assertTrue(self._indexed(facility))

        facility.is_candidate = True
        facility.save()

        self.assertFalse(self._indexed(facility))

    def test_updating_a_candidate_does_not_index_it(self):
        candidate = self._create_candidate()

        candidate.confidence = 0.95
        candidate.save()

        self.assertFalse(self._indexed(candidate))

    def test_deleting_a_graduated_facility_removes_it(self):
        candidate = self._create_candidate()
        candidate.is_candidate = False
        candidate.save()
        self.assertTrue(self._indexed(candidate))

        facility_id = candidate.id
        candidate.delete()

        self.assertFalse(FacilityIndex.objects.filter(id=facility_id).exists())

    def test_deleting_a_candidate_leaves_no_index_row(self):
        candidate = self._create_candidate()
        facility_id = candidate.id

        candidate.delete()

        self.assertFalse(FacilityIndex.objects.filter(id=facility_id).exists())

    def test_bulk_reindex_excludes_candidates(self):
        facility = self._create_facility()
        candidate = self._create_candidate()

        index_facilities_new([])

        self.assertTrue(self._indexed(facility))
        self.assertFalse(self._indexed(candidate))

    def test_targeted_reindex_excludes_candidates(self):
        facility = self._create_facility()
        candidate = self._create_candidate()

        index_facilities_new([facility.id, candidate.id])

        self.assertTrue(self._indexed(facility))
        self.assertFalse(self._indexed(candidate))

    def test_targeted_reindex_removes_a_stale_candidate_row(self):
        """
        A candidate row that somehow reached the index (e.g. written before
        0246) is cleaned up the next time its id is re-indexed, the same
        way a deleted facility's row is.
        """
        candidate = self._create_candidate()
        confirmed = self._create_facility()
        stale = FacilityIndex.objects.get(id=confirmed.id)
        stale.pk = candidate.id
        stale.id = candidate.id
        stale.uuid = candidate.uuid
        stale.save(force_insert=True)
        self.assertTrue(self._indexed(candidate))

        index_facilities_new([candidate.id])

        self.assertFalse(self._indexed(candidate))
