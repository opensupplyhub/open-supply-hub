"""
Candidate facilities are never match targets (OSDEV-3243).

`api_facility.is_candidate` marks unconfirmed satellite detections (Earth
Genome). Matching is one-directional: a contributor upload must never be
matched to a candidate, so no FacilityMatch to a candidate is ever created by
dedupe-hub. These tests run the real match-target queries against an
in-memory SQLite copy of the tables so the exclusion is checked on actual
rows rather than on mocked query chains.
"""
import unittest
from datetime import datetime
from unittest.mock import patch

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON, Column, MetaData, Table, Text, create_engine, event
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Session

from app.database.models.facility import Facility
from app.database.sqlalchemy import Base
from app.matching.matcher.exact.exact_matcher import ExactMatcher
from app.matching.matcher.gazeteer.gazetteer_cache import GazetteerCache
from app.matching.matcher.gazeteer.gazetteer_data_fetcher import (
    get_canonical_items,
)
from app.matching.matcher.gazeteer.gazetteer_matcher import GazetteerMatcher

MATCHING = 'app.matching.matcher'
SESSION_TARGETS = (
    MATCHING + '.exact.exact_matcher.get_session',
    MATCHING + '.gazeteer.gazetteer_cache.get_session',
    MATCHING + '.gazeteer.gazetteer_data_fetcher.get_session',
    MATCHING + '.gazeteer.gazetteer_matcher.get_session',
)
# PostGIS functions geoalchemy2 wraps geometry columns in. SQLite has none,
# so they are registered as pass-throughs; no test reads a geometry back.
GEOMETRY_FUNCTIONS = (
    'ST_AsEWKB', 'AsEWKB', 'ST_GeomFromEWKT', 'GeomFromEWKT',
)


class SQLiteDatabase:
    """
    An in-memory SQLite database holding a copy of every table in the
    SQLAlchemy metadata, with the Postgres-only column types (PostGIS
    geometry, arrays, jsonb) replaced by types SQLite can store. Rows are
    written through the shadow tables so the Postgres bind processors of the
    mapped models are not involved; the production queries then read them
    through the real models.
    """

    def __init__(self):
        self.engine = create_engine('sqlite://')
        event.listen(self.engine, 'connect', self._register_functions)
        self.metadata = MetaData()
        for table in Base.metadata.tables.values():
            Table(table.name, self.metadata, *[
                Column(
                    column.name,
                    self._portable_type(column.type),
                    primary_key=column.primary_key,
                    nullable=column.nullable,
                    server_default=column.server_default,
                )
                for column in table.columns
            ])
        self.metadata.create_all(self.engine)

    @staticmethod
    def _register_functions(dbapi_connection, _record):
        for name in GEOMETRY_FUNCTIONS:
            dbapi_connection.create_function(name, 1, lambda value: value)
            dbapi_connection.create_function(
                name, 2, lambda value, _srid: value
            )

    @staticmethod
    def _portable_type(column_type):
        if isinstance(column_type, (Geometry, ARRAY)):
            return Text()
        if isinstance(column_type, JSONB):
            return JSON()
        return column_type

    def session(self):
        return Session(self.engine)

    def insert(self, table_name, **values):
        with self.engine.begin() as connection:
            connection.execute(
                self.metadata.tables[table_name].insert(), values
            )

    def update(self, table_name, where, **values):
        table = self.metadata.tables[table_name]
        with self.engine.begin() as connection:
            connection.execute(table.update().where(
                *[table.c[key] == value for key, value in where.items()]
            ), values)


class CandidateExclusionTestCase(unittest.TestCase):
    CONFIRMED_ID = 'US2024001ABCDEF'
    CANDIDATE_ID = 'US2024002CANDID'

    def setUp(self):
        self.db = SQLiteDatabase()
        for target in SESSION_TARGETS:
            patcher = patch(target, side_effect=self.db.session)
            patcher.start()
            self.addCleanup(patcher.stop)
        GazetteerCache._gazetter = None
        GazetteerCache._facility_version = None
        GazetteerCache._match_version = None

        self.add_facility(self.CONFIRMED_ID, name='Acme Mill',
                          address='1 Main St')
        self.add_facility(self.CANDIDATE_ID, name='', address='',
                          is_candidate=True, source='earth_genome',
                          external_id='eg-1', confidence=0.9)

    def add_facility(self, facility_id, **values):
        row = {
            'id': facility_id,
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': None,
            'created_from_id': 1,
            'has_inexact_coordinates': False,
            'is_candidate': False,
            'source': '',
        }
        row.update(values)
        self.db.insert('api_facility', **row)

    def add_list_item(self, item_id, facility_id, name='Acme Mill',
                      address='1 Main St', status='MATCHED'):
        self.db.insert(
            'api_facilitylistitem',
            id=item_id, source_id=1, row_index=item_id, status=status,
            name=name, address=address, country_code='US',
            clean_name=name.lower(), clean_address=address.lower(),
            geocoded_address='', facility_id=facility_id, sector='{}',
            processing_started_at=datetime(2024, 1, 1),
            processing_completed_at=datetime(2024, 1, 1),
        )

    def add_match(self, match_id, item_id, facility_id, status='CONFIRMED'):
        self.db.insert(
            'api_facilitymatch',
            id=match_id, facility_list_item_id=item_id,
            facility_id=facility_id, status=status, is_active=True,
            confidence=1,
        )

    def add_facility_history(self, history_id, facility_id,
                             history_type='+'):
        self.db.insert(
            'api_historicalfacility',
            id=facility_id, name='', address='', country_code='US',
            history_id=history_id, history_type=history_type,
        )

    def add_match_history(self, history_id, match_id, facility_id,
                          history_type='+'):
        self.db.insert(
            'api_historicalfacilitymatch',
            id=match_id, facility_id=facility_id,
            history_id=history_id, history_type=history_type,
        )

    def graduate_candidate(self):
        self.db.update(
            'api_facility', {'id': self.CANDIDATE_ID},
            is_candidate=False, name='Graduated Mill', address='2 Main St',
        )


class TestFacilityModel(CandidateExclusionTestCase):
    def test_facility_created_by_dedupe_hub_is_not_a_candidate(self):
        """
        CumulativeMatcher creates a Facility for every unmatched list item
        through this model without setting the candidate columns, so they
        must default to a confirmed facility.
        """
        with self.db.session() as session:
            facility = Facility()
            facility.id = 'US2024003NEWONE'
            facility.name = 'New'
            facility.address = '3 Main St'
            facility.country_code = 'US'
            facility.location = 'POINT(0 0)'
            facility.created_from_id = 3
            session.add(facility)
            session.commit()

        with self.db.session() as session:
            row = session.query(
                Facility.is_candidate, Facility.source, Facility.polygon,
                Facility.confidence, Facility.external_id,
            ).filter(Facility.id == 'US2024003NEWONE').one()
        self.assertEqual(
            tuple(row), (False, '', None, None, None)
        )

    def test_candidate_columns_match_the_django_model(self):
        columns = Facility.__table__.columns
        self.assertFalse(columns['is_candidate'].nullable)
        self.assertIs(columns['is_candidate'].default.arg, False)
        self.assertTrue(columns['polygon'].nullable)
        self.assertEqual(columns['polygon'].type.geometry_type, 'POLYGON')
        self.assertEqual(columns['polygon'].type.srid, 4326)
        self.assertTrue(columns['confidence'].nullable)
        self.assertTrue(columns['external_id'].nullable)
        self.assertFalse(columns['source'].nullable)
        self.assertEqual(columns['source'].default.arg, '')


class TestGazetteerCanonicalItems(CandidateExclusionTestCase):
    def test_candidates_are_not_canonical_items(self):
        items = get_canonical_items()

        self.assertIn(self.CONFIRMED_ID, items)
        self.assertNotIn(self.CANDIDATE_ID, items)

    def test_confirmed_matches_to_candidates_are_not_canonical_items(self):
        self.add_list_item(11, self.CONFIRMED_ID)
        self.add_match(1, 11, self.CONFIRMED_ID)
        self.add_list_item(12, self.CANDIDATE_ID, name='', address='')
        self.add_match(2, 12, self.CANDIDATE_ID)

        items = get_canonical_items()

        self.assertEqual(
            set(items), {self.CONFIRMED_ID, self.CONFIRMED_ID + '_MATCH-1'}
        )

    def test_graduated_candidate_becomes_a_canonical_item(self):
        self.graduate_candidate()

        items = get_canonical_items()

        self.assertEqual(set(items), {self.CONFIRMED_ID, self.CANDIDATE_ID})
        self.assertEqual(items[self.CANDIDATE_ID]['name'], 'graduated mill')


class TestGazetteerIncrementalIndex(CandidateExclusionTestCase):
    def test_new_candidate_is_not_indexed_but_marker_advances(self):
        self.add_facility_history(1, self.CONFIRMED_ID)
        self.add_facility_history(2, self.CANDIDATE_ID)

        changes, records = GazetteerCache._get_new_facility_history()

        self.assertEqual([c['history_id'] for c in changes], [1, 2])
        self.assertEqual(set(records), {self.CONFIRMED_ID})

    def test_graduated_candidate_is_indexed(self):
        self.graduate_candidate()
        self.add_facility_history(1, self.CANDIDATE_ID, history_type='~')

        _changes, records = GazetteerCache._get_new_facility_history()

        self.assertEqual(set(records), {self.CANDIDATE_ID})

    def test_candidate_matches_are_not_indexed(self):
        self.add_list_item(11, self.CONFIRMED_ID)
        self.add_match(1, 11, self.CONFIRMED_ID)
        self.add_list_item(12, self.CANDIDATE_ID, name='', address='')
        self.add_match(2, 12, self.CANDIDATE_ID)
        self.add_match_history(1, 1, self.CONFIRMED_ID)
        self.add_match_history(2, 2, self.CANDIDATE_ID)

        changes, records, existing_facility_ids = \
            GazetteerCache._get_new_match_history()

        self.assertEqual(len(changes), 2)
        self.assertEqual(existing_facility_ids, {self.CONFIRMED_ID})
        # `get_latest` only indexes a match whose facility is in
        # `existing_facility_ids`, so the candidate's match never reaches
        # the gazetteer even though its record was fetched.
        self.assertIn(2, records)


class TestGazetteerMatcher(CandidateExclusionTestCase):
    def test_facility_exists_rejects_candidates(self):
        matcher = GazetteerMatcher()

        self.assertTrue(matcher.facility_exists(self.CONFIRMED_ID))
        self.assertFalse(matcher.facility_exists(self.CANDIDATE_ID))
        self.assertFalse(
            matcher.facility_exists(self.CANDIDATE_ID + '_MATCH-2')
        )
        self.assertFalse(matcher.facility_exists('US2024009MISSIN'))

    def test_filter_matches_drops_stale_candidate_matches(self):
        """
        The gazetteer never unindexes, so a facility that reverted to a
        candidate can still come back from Dedupe. It must be dropped the
        same way a deleted facility is.
        """
        matcher = GazetteerMatcher()
        results = [[
            (('101', self.CONFIRMED_ID), 0.8),
            (('101', self.CANDIDATE_ID), 0.99),
            (('102', self.CANDIDATE_ID + '_MATCH-2'), 0.99),
        ]]

        matches = matcher.filter_matches(results)

        self.assertEqual(
            [m['facility_id'] for m in matches['101']], [self.CONFIRMED_ID]
        )
        self.assertNotIn('102', matches)

    def test_no_gazetteer_matches_when_only_candidates_exist(self):
        self.db.update('api_facility', {'id': self.CONFIRMED_ID},
                       is_candidate=True)
        matcher = GazetteerMatcher()

        self.assertEqual(matcher.gazetter_match({}), [])
        self.assertTrue(matcher.no_gazetteer_matches)


class TestExactMatcher(CandidateExclusionTestCase):
    MESSY = {'name': 'acme mill', 'address': '1 main st', 'country': 'us'}

    def test_items_matched_to_candidates_are_not_exact_matches(self):
        self.add_list_item(11, self.CONFIRMED_ID)
        self.add_list_item(12, self.CANDIDATE_ID)

        items = ExactMatcher.get_matched_items(self.MESSY)

        self.assertEqual([item.id for item in items], [11])

    def test_empty_upload_does_not_exact_match_a_candidate(self):
        """
        A candidate's synthetic list item carries the empty-string name
        and address sentinel, so without the exclusion any upload with an
        empty name and address would be an exact match for it.
        """
        self.add_list_item(12, self.CANDIDATE_ID, name='', address='')

        items = ExactMatcher.get_matched_items(
            {'name': '', 'address': '', 'country': 'us'}
        )

        self.assertEqual(items, [])

    def test_graduated_candidate_is_an_exact_match_target(self):
        self.graduate_candidate()
        self.add_list_item(12, self.CANDIDATE_ID)

        items = ExactMatcher.get_matched_items(self.MESSY)

        self.assertEqual([item.id for item in items], [12])

    def test_exact_matches_carry_the_confirmed_facility_only(self):
        self.add_list_item(11, self.CONFIRMED_ID)
        self.add_list_item(12, self.CANDIDATE_ID)

        matches = ExactMatcher().get_exact_matches(self.MESSY)

        self.assertEqual(
            [m['facility_id'] for m in matches], [self.CONFIRMED_ID]
        )
