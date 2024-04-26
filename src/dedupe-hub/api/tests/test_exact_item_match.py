import unittest
from unittest.mock import MagicMock, patch
from app.matching.matcher.exact.exact_item_match import ExactItemMatch
from app.database.models.facility_list_item_temp import FacilityListItemTemp


class TestExactItemMatch(unittest.TestCase):
    def setUp(self):
        self.item_id = 1
        self.started = "2024-04-25 12:00:00"
        self.finished = "2024-04-25 12:10:00"
        self.results = {}
        self.automatic_threshold = 1.0

        self.matches_empty = []
        self.matches_single = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
        ]
        self.matches_multiple = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
            {"id": 2073, "facility_id": "CN20241096SFEBA", "score": "1"},
            {"id": 2074, "facility_id": "CN20241096SFEBA", "score": "1"},
        ]

        # Setup mock for database session in BaseItemMatch
        self.session_patcher = patch(
            'app.matching.matcher.base_item_match.get_session'
        )
        self.mock_session = self.session_patcher.start()
        self.mock_query = (
            self.mock_session.return_value.__enter__.return_value.query
        )
        self.mock_item = MagicMock(
            spec=FacilityListItemTemp,
            id=self.item_id,
        )
        # Setup the return values for query
        self.mock_query.return_value.get.return_value = self.mock_item

    def tearDown(self):
        self.session_patcher.stop()

    def create_exact_match(self, matches):
        return ExactItemMatch(
            self.item_id,
            matches,
            self.started,
            self.finished,
            self.results,
            self.automatic_threshold,
        )

    def expected_result_dict(self, match_type):
        return [
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBA',
                'status': 'AUTOMATIC',
                'results': {'match_type': match_type},
                'confidence': 1,
            }
        ]

    def setup_session_mock(self, get_session_mock, return_value):
        session_mock = MagicMock()
        session_mock.query().filter().scalar.return_value = return_value
        get_session_mock.return_value.__enter__.return_value = session_mock

    def test_process_no_matches(self):
        exact_match = self.create_exact_match(self.matches_empty)
        result = exact_match.process()

        self.assertEqual(result, [])

    @patch('app.matching.matcher.exact.exact_item_match.get_session')
    def test_process_with_single_match(self, get_session_mock):
        self.setup_session_mock(get_session_mock, True)

        exact_match = self.create_exact_match(self.matches_single)
        result = exact_match.process()
        expected_result = self.expected_result_dict('single_exact_match')

        self.assertEqual(result, expected_result)
        self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)

    @patch('app.matching.matcher.exact.exact_item_match.get_session')
    def test_process_with_multiple_matches(self, get_session_mock):
        self.setup_session_mock(get_session_mock, True)

        exact_match = self.create_exact_match(self.matches_multiple)
        result = exact_match.process()
        expected_result = self.expected_result_dict('multiple_exact_matches')

        self.assertEqual(result, expected_result)
        self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)

    @patch('app.matching.matcher.exact.exact_item_match.get_session')
    def test_process_without_session(self, get_session_mock):
        self.setup_session_mock(get_session_mock, False)

        exact_match = self.create_exact_match(self.matches_multiple)
        result = exact_match.process()

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
