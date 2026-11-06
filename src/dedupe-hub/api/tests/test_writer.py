"""
The Writer commits each item's match rows and final status together
(OSDEV-3149).

Django answers `POST /api/facilities/` by polling the list item's status and
reading its matches once the status is final. When the status was committed
before the matches, and the matches one row at a time, that read could return
`MATCHED` with only the pending matches and no `os_id`. These tests run the
Writer against an in-memory SQLite copy of the tables.
"""
import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy import select

from app.config import settings
from app.matching.writer import Writer
from tests.test_candidate_exclusion import SQLiteDatabase

ITEM_ID = 10
SOURCE_ID = 1
MATCHED_FACILITY = 'CN2025009ZBDG5F'
PENDING_FACILITIES = ('CN20231539A6A6A', 'CN2022336DYYP24')
NEW_FACILITY = 'CN2026308NEWFAC'


class WriterTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDatabase()
        patcher = patch(
            'app.matching.writer.get_session', side_effect=self.db.session
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        index_patcher = patch.object(Writer, '_index_facilities')
        self.index_facilities = index_patcher.start()
        self.addCleanup(index_patcher.stop)

        live_patcher = patch.object(settings, 'dedupe_hub_live', True)
        live_patcher.start()
        self.addCleanup(live_patcher.stop)

        for facility_id in (MATCHED_FACILITY,) + PENDING_FACILITIES:
            self.db.insert(
                'api_facility', id=facility_id, name='Mill', address='Road',
                country_code='CN', created_from_id=1,
                has_inexact_coordinates=False, is_candidate=False, source='',
            )

    def add_item(self, create):
        self.db.insert(
            'api_source', id=SOURCE_ID, contributor_id=1,
            facility_list_id=1, is_active=True, create=create,
        )
        item = dict(
            id=ITEM_ID, source_id=SOURCE_ID, row_index=0, status='GEOCODED',
            name='Jiangsu Jianhua Textile', address='211 Huaihai East Road',
            country_code='CN', clean_name='jiangsu jianhua textile',
            clean_address='211 huaihai east road', geocoded_address='',
            sector='{}', processing_results=[],
            processing_started_at=datetime(2026, 7, 29),
            processing_completed_at=datetime(2026, 7, 29),
        )
        self.db.insert('api_facilitylistitem', **item)
        self.db.insert('api_facilitylistitemtemp', **item)

    @staticmethod
    def match(facility_id, confidence, status):
        return {
            'facility_list_item_id': ITEM_ID,
            'facility_id': facility_id,
            'confidence': confidence,
            'status': status,
            'results': {},
        }

    def gazetteer_matches(self):
        # The order GazetteerItemMatch returns them in: pending first, the
        # automatic match last.
        return [
            self.match(PENDING_FACILITIES[0], 0.54, 'PENDING'),
            self.match(PENDING_FACILITIES[1], 0.53, 'PENDING'),
            self.match(MATCHED_FACILITY, 0.89, 'AUTOMATIC'),
        ]

    @staticmethod
    def item_update(status, facility_id, new_facility=None):
        return {
            ITEM_ID: {
                'facility_list_item_id': ITEM_ID,
                'source_id': SOURCE_ID,
                'status': status,
                'facility_id': facility_id,
                'processing_results': [{'action': 'match', 'error': False}],
                'new_facility': new_facility,
            }
        }

    def rows(self, table_name, *columns):
        table = self.db.metadata.tables[table_name]
        with self.db.engine.connect() as connection:
            return connection.execute(
                select(*[table.c[column] for column in columns])
            ).all()

    def item_state(self, table_name):
        return self.rows(table_name, 'status', 'facility_id')[0]

    def test_status_and_matches_are_written_together(self):
        self.add_item(create=False)

        written = Writer().write(
            self.gazetteer_matches(),
            self.item_update('MATCHED', MATCHED_FACILITY),
        )

        self.assertEqual(len(written), 3)
        self.assertEqual(
            self.item_state('api_facilitylistitemtemp'),
            ('MATCHED', MATCHED_FACILITY),
        )
        self.assertCountEqual(
            self.rows('api_facilitymatchtemp', 'facility_id', 'status'),
            [
                (PENDING_FACILITIES[0], 'PENDING'),
                (PENDING_FACILITIES[1], 'PENDING'),
                (MATCHED_FACILITY, 'AUTOMATIC'),
            ],
        )

    def test_each_item_is_committed_once(self):
        self.add_item(create=False)
        commits = []
        original_session = self.db.session

        def counting_session():
            session = original_session()
            commit = session.commit
            session.commit = lambda: (commits.append(1), commit())[1]
            return session

        with patch('app.matching.writer.get_session',
                   side_effect=counting_session):
            Writer().write(
                self.gazetteer_matches(),
                self.item_update('MATCHED', MATCHED_FACILITY),
            )

        self.assertEqual(len(commits), 1)

    def test_item_already_matched_is_not_written_again(self):
        """
        Two dedupe-hub tasks can both process the same message. The second
        write must not add a second set of matches: two AUTOMATIC rows make
        Django answer MATCHED without an os_id.
        """
        self.add_item(create=False)

        Writer().write(
            self.gazetteer_matches(),
            self.item_update('MATCHED', MATCHED_FACILITY),
        )
        written = Writer().write(
            self.gazetteer_matches(),
            self.item_update('MATCHED', MATCHED_FACILITY),
        )

        self.assertEqual(written, [])
        self.assertEqual(len(self.rows('api_facilitymatchtemp', 'id')), 3)

    def test_non_create_source_leaves_origin_tables_alone(self):
        self.add_item(create=False)

        Writer().write(
            self.gazetteer_matches(),
            self.item_update('MATCHED', MATCHED_FACILITY),
        )

        self.assertEqual(self.rows('api_facilitymatch', 'id'), [])
        self.assertEqual(
            self.item_state('api_facilitylistitem'), ('GEOCODED', None)
        )
        self.index_facilities.assert_called_once_with(
            {MATCHED_FACILITY} | set(PENDING_FACILITIES)
        )

    def test_create_source_writes_origin_tables(self):
        self.add_item(create=True)
        self.db.insert(
            'api_extendedfield', id=1, contributor_id=1,
            facility_list_item_id=ITEM_ID, is_verified=False,
            field_name='number_of_workers',
        )

        Writer().write(
            self.gazetteer_matches(),
            self.item_update('MATCHED', MATCHED_FACILITY),
        )

        self.assertEqual(
            self.item_state('api_facilitylistitem'),
            ('MATCHED', MATCHED_FACILITY),
        )
        self.assertEqual(len(self.rows('api_facilitymatch', 'id')), 3)
        self.assertEqual(
            self.rows('api_extendedfield', 'facility_id'),
            [(MATCHED_FACILITY,)],
        )

    def test_create_source_new_facility_is_written_with_its_match(self):
        self.add_item(create=True)

        Writer().write(
            [self.match(NEW_FACILITY, 1, 'AUTOMATIC')],
            self.item_update('MATCHED', NEW_FACILITY, new_facility={
                'id': NEW_FACILITY,
                'name': 'Jiangsu Jianhua Textile',
                'address': '211 Huaihai East Road',
                'country_code': 'CN',
                'location': None,
                'created_from_id': ITEM_ID,
            }),
        )

        self.assertIn(
            (NEW_FACILITY, ITEM_ID),
            self.rows('api_facility', 'id', 'created_from_id'),
        )
        self.assertEqual(
            self.rows('api_facilitymatch', 'facility_id', 'status'),
            [(NEW_FACILITY, 'AUTOMATIC')],
        )
        self.assertEqual(
            self.item_state('api_facilitylistitem'),
            ('MATCHED', NEW_FACILITY),
        )

    def test_new_facility_is_not_created_for_an_item_already_matched(self):
        self.add_item(create=True)
        self.db.update(
            'api_facilitylistitemtemp', {'id': ITEM_ID}, status='MATCHED'
        )

        Writer().write(
            [self.match(NEW_FACILITY, 1, 'AUTOMATIC')],
            self.item_update('MATCHED', NEW_FACILITY, new_facility={
                'id': NEW_FACILITY,
                'name': 'Jiangsu Jianhua Textile',
                'address': '211 Huaihai East Road',
                'country_code': 'CN',
                'location': None,
                'created_from_id': ITEM_ID,
            }),
        )

        self.assertNotIn(
            (NEW_FACILITY,), self.rows('api_facility', 'id')
        )
        self.index_facilities.assert_not_called()


if __name__ == '__main__':
    unittest.main()
