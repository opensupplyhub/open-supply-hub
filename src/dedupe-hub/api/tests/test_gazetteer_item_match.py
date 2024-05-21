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
        )
        self.mock_facility = MagicMock(
            spec=Facility,
            id=self.facility_id,
        )
        # Setup the return values for query
        self.mock_query.return_value.get.return_value = self.mock_item
        self.mock_query_gazetteer.return_value.one.return_value = self.mock_facility

    def tearDown(self):
        self.session_patcher.stop()

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

if __name__ == '__main__':
    unittest.main()