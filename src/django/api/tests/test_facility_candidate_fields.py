import uuid

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)

from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'


class FacilityCandidateFieldsTest(TestCase):
    """Tests for the candidate columns added to Facility (OSDEV-3242)."""

    def setUp(self):
        self.user = User.objects.create(email='one@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
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
        """Each Facility needs its own list item (created_from is 1:1)."""
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

    def test_candidate_facility_saves_and_gets_normal_os_id(self):
        """A candidate with an empty name/address saves via the ORM."""
        facility = self._create_candidate()
        facility.refresh_from_db()

        self.assertTrue(facility.id.startswith('US'))
        self.assertEqual(len(facility.id), 15)
        self.assertTrue(facility.is_candidate)
        self.assertEqual(facility.source, 'earth_genome')
        self.assertEqual(facility.external_id, 'eg-facility-0001')
        self.assertEqual(facility.confidence, 0.87)
        self.assertEqual(
            facility.polygon, GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326)
        )

    def test_same_source_and_external_id_cannot_be_ingested_twice(self):
        """Re-ingesting the same external row violates the unique key."""
        self._create_candidate(external_id='eg-facility-0002')

        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                self._create_candidate(external_id='eg-facility-0002')

        self.assertIn(
            'api_facility_source_external_id_uniq', str(ctx.exception)
        )

    def test_sourced_facility_requires_external_id(self):
        """A row claiming an external source must carry that source's id.

        The unique constraint treats NULL external_id values as distinct,
        so only the CHECK constraint stops a sourced row from being
        re-ingested without an id.
        """
        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                self._create_candidate(external_id=None)

        self.assertIn(
            'api_facility_source_requires_external_id', str(ctx.exception)
        )

    def test_unsourced_facilities_coexist_without_external_id(self):
        """Normal facilities all share (source='', external_id=None).

        The unique index treats NULLs as distinct, which every facility
        created through the normal contribution flow relies on.
        """
        first = self._create_facility()
        second = self._create_facility()

        for facility in (first, second):
            facility.refresh_from_db()
            self.assertEqual(facility.source, '')
            self.assertIsNone(facility.external_id)
        self.assertEqual(Facility.objects.count(), 2)

    def test_raw_insert_with_only_legacy_columns_still_succeeds(self):
        """An INSERT naming only pre-candidate columns must keep working.

        dedupe-hub writes api_facility through its own SQLAlchemy model
        (see src/dedupe-hub/api/app/matching/matcher/cumulative_matcher.py)
        that predates the candidate columns, so migration 0235 keeps DB
        defaults for is_candidate and source on purpose. Do not "fix" a
        failure here by dropping those DB defaults — teach dedupe-hub the
        new schema instead (OSDEV-3243).
        """
        list_item = self._create_list_item()
        facility_id = 'US2026123AAAAA'

        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO api_facility (
                    id, name, address, country_code, location,
                    created_from_id, has_inexact_coordinates,
                    created_at, updated_at, uuid
                )
                VALUES (
                    %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(0, 0), 4326),
                    %s, false, now(), now(), %s
                )
                ''',
                [
                    facility_id,
                    'Raw Name',
                    'Raw Address',
                    'US',
                    list_item.id,
                    str(uuid.uuid4()),
                ],
            )

        facility = Facility.objects.get(id=facility_id)
        self.assertFalse(facility.is_candidate)
        self.assertEqual(facility.source, '')
        self.assertIsNone(facility.external_id)
        self.assertIsNone(facility.polygon)
        self.assertIsNone(facility.confidence)

    def test_candidate_fields_are_mirrored_into_history(self):
        """Saving a candidate writes its fields to HistoricalFacility."""
        facility = self._create_candidate()

        history = facility.history.first()

        self.assertTrue(history.is_candidate)
        self.assertEqual(history.source, 'earth_genome')
        self.assertEqual(history.external_id, 'eg-facility-0001')
        self.assertEqual(history.confidence, 0.87)
        self.assertEqual(
            history.polygon, GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326)
        )

    def test_facility_without_candidate_kwargs_defaults_to_non_candidate(
        self,
    ):
        """The ORM path keeps normal facilities untouched by the change."""
        facility = self._create_facility()
        facility.refresh_from_db()

        self.assertFalse(facility.is_candidate)
        self.assertEqual(facility.source, '')
        self.assertIsNone(facility.external_id)
        self.assertIsNone(facility.polygon)
        self.assertIsNone(facility.confidence)
