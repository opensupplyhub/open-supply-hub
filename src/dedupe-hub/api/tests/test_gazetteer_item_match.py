import unittest
from unittest.mock import MagicMock, patch
from app.matching.matcher.gazeteer.gazetteer_item_match import GazetteerItemMatch
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility import Facility


class TestGazetteerItemMatch(unittest.TestCase):
    def setUp(self):
        self.item_id = 1
        self.facility_id = "CN20241096SFEBA"
        self.started = "2024-04-25 12:00:00"
        self.finished = "2024-04-25 12:10:00"
        self.results = {}
        self.automatic_threshold = 0.8

        self.matches_empty = []
        self.matches_single = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": 1},
        ]
        self.matches_multiple = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": 0.75},
            {"id": 2073, "facility_id": "CN20241096SFEBB", "score": 0.90},
        ]

        self.matches_multiple_second = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": 0.85},
            {"id": 2073, "facility_id": "CN20241096SFEBB", "score": 0.90},
        ]

        # Setup mock for database session in BaseItemMatch
        self.session_patcher = patch(
            'app.matching.matcher.base_item_match.get_session'
        )
        # Setup mock for database session in BaseItemMatch
        self.session_patcher_gazetteer = patch(
            'app.matching.matcher.gazeteer.gazetteer_item_match.get_session'
        )
        self.mock_session = self.session_patcher.start()
        self.mock_session_gazetteer = self.session_patcher_gazetteer.start()
        self.mock_query = (
            self.mock_session.return_value.__enter__.return_value.query
        )
        self.mock_query_gazetteer = (
            self.mock_session_gazetteer.return_value.__enter__.return_value.query
        )
        self.mock_item = MagicMock(
            spec=FacilityListItemTemp,
            id=self.item_id,
            processing_results=[],
            facility_id=None,
        )
        self.mock_facility = MagicMock(
            spec=Facility,
            id=self.facility_id,
        )
        # Setup the return values for query
        self.mock_query.return_value.get.return_value = self.mock_item
        self.mock_query_gazetteer.return_value.one.return_value = self.mock_facility
        self.mock_query_gazetteer.return_value.filter.return_value \
            .one.return_value = self.mock_facility

    def tearDown(self):
        self.session_patcher.stop()
        self.session_patcher_gazetteer.stop()

    def create_gazetteer_match(self, matches):
        return GazetteerItemMatch(
            self.item_id,
            matches,
            self.started,
            self.finished,
            self.results,
            self.automatic_threshold,
        )

    def test_single_gazetter(self):
        gazetteer_match = self.create_gazetteer_match(self.matches_single)

        result = gazetteer_match.process()
        expected_result = [
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBA',
                'status': 'AUTOMATIC',
                'results': {'match_type': 'single_gazetteer_match'},
                'confidence': 1,
            }
        ]

        self.assertListEqual(result, expected_result)
        self.assert_staged_update(
            gazetteer_match, FacilityListItemTemp.MATCHED, self.facility_id
        )
    
    def test_one_gazetter_greater(self):
        gazetteer_match = self.create_gazetteer_match(self.matches_multiple)

        result = gazetteer_match.process()
        expected_result = [
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBA',
                'status': 'PENDING',
                'results': {},
                'confidence': 0.75,
            },
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBB',
                'status': 'AUTOMATIC',
                'results': {'match_type': 'one_gazetteer_match_greater_than_threshold'},
                'confidence': 0.90,
            }
        ]

        self.assertListEqual(result, expected_result)
        self.assert_staged_update(
            gazetteer_match, FacilityListItemTemp.MATCHED, self.facility_id
        )

    def test_no_automatic_match_stages_potential_match(self):
        gazetteer_match = self.create_gazetteer_match([
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": 0.54},
            {"id": 2073, "facility_id": "CN20241096SFEBB", "score": 0.53},
        ])

        result = gazetteer_match.process()

        self.assertEqual(
            [match['status'] for match in result], ['PENDING', 'PENDING']
        )
        self.assert_staged_update(
            gazetteer_match, FacilityListItemTemp.POTENTIAL_MATCH, None
        )

    def test_no_matches_stages_nothing(self):
        gazetteer_match = self.create_gazetteer_match(self.matches_empty)

        self.assertEqual(gazetteer_match.process(), [])
        self.assertIsNone(gazetteer_match.pending_item_update)

    def test_multiple_gazetteer(self):
        gazetteer_match = self.create_gazetteer_match(self.matches_multiple_second)

        string_matched_mock = MagicMock()
        string_matched_mock.side_effect = [True, False]
        gazetteer_match.string_matched = string_matched_mock

        result = gazetteer_match.process()
        expected_result = [
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBB',
                'status': 'PENDING',
                'results': {},
                'confidence': 0.9,
            },
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBA',
                'status': 'AUTOMATIC',
                'results': {'match_type': 'multiple_gazetteer_matches_with_one_exact_string_match'},
                'confidence': 0.85,
            }
        ]

        self.assertListEqual(result, expected_result)

    def assert_staged_update(self, gazetteer_match, status, facility_id):
        """
        The final status is staged for the Writer, which commits it with
        the match rows; it is not written here (OSDEV-3149).
        """
        update = gazetteer_match.pending_item_update
        self.assertEqual(update['facility_list_item_id'], self.item_id)
        self.assertEqual(update['status'], status)
        self.assertEqual(update['facility_id'], facility_id)
        self.assertEqual(update['processing_results'][-1]['action'], 'match')
        self.mock_session.return_value.__enter__.return_value \
            .commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
