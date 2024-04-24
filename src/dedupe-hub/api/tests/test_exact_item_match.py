import unittest
from unittest.mock import MagicMock, patch

from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.matching.matcher.exact.exact_item_match import ExactItemMatch


class TestExactItemMatch(unittest.TestCase):

    def setUp(self):
        self.item_id = 1
        self.matches_empty = []
        self.matches_single = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
        ]
        self.matches_multiple = [
            {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
            {"id": 2073, "facility_id": "CN20241096SFEBA", "score": "1"},
            {"id": 2074, "facility_id": "CN20241096SFEBA", "score": "1"},
        ]
        self.started = "2024-04-22 10:57:29.258354"
        self.finished = "2024-04-22 10:57:29.263924"
        self.results = {}
        self.automatic_threshold = 1.0

    # @patch('app.database.sqlalchemy.get_session')
    # def test_process_with_no_matches(self, get_session_mock):
    #     session_mock = MagicMock()
    #     session_mock.query().filter().scalar.return_value = False
    #     get_session_mock.return_value.__enter__.return_value = session_mock

    #     exact_match = ExactItemMatch(
    #         self.item_id,
    #         self.matches_empty,
    #         self.started,
    #         self.finished,
    #         self.results,
    #         self.automatic_threshold,
    #     )

    #     result = exact_match.process()
    #     expected_result = []

    #     self.assertEqual(result, expected_result)
    #     self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)

    @patch('app.database.sqlalchemy.get_session')
    @patch('app.database.models.facility.Facility')
    @patch('app.database.models.source.Source')
    def test_process_with_one_match(
        self, facility_mock, get_session_mock, source_mock
    ):
        facility_mock.query().filter().scalar.return_value = True
        source_mock.query().filter().scalar.return_value = True
        # Mocking session query to return False
        session_mock = MagicMock()
        session_mock.query().filter().scalar.return_value = False
        get_session_mock.return_value.__enter__.return_value = session_mock

        exact_match = ExactItemMatch(
            self.item_id,
            self.matches_single,
            self.started,
            self.finished,
            self.results,
            self.automatic_threshold,
        )

        result = exact_match.process()
        expected_result = [
            {
                'facility_list_item_id': 1,
                'facility_id': 'CN20241096SFEBA',
                'status': 'AUTOMATIC',
                'results': {'match_type': 'single_exact_match'},
                'confidence': 1,
            }
        ]

        self.assertEqual(result, expected_result)
        self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)

    # @patch('app.database.models.facility.Facility')
    # def test_process_with_multiple_matches(self, facility_mock):
    #     facility_mock.query().filter().scalar.return_value = True

    #     exact_match = ExactItemMatch(
    #         self.item_id,
    #         self.matches_multiple,
    #         self.started,
    #         self.finished,
    #         self.results,
    #         self.automatic_threshold,
    #     )

    #     result = exact_match.process()
    #     expected_result = [
    #         {
    #             'facility_list_item_id': 1,
    #             'facility_id': 'CN20241096SFEBA',
    #             'status': 'AUTOMATIC',
    #             'results': {'match_type': 'multiple_exact_matches'},
    #             'confidence': 1,
    #         }
    #     ]

    #     self.assertEqual(result, expected_result)
    #     self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)


if __name__ == '__main__':
    unittest.main()
