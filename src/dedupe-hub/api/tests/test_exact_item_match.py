import unittest
from unittest.mock import patch

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

    def test_process_no_matches(self):
        exact_match = ExactItemMatch(
            self.item_id,
            self.matches_empty,
            self.started,
            self.finished,
            self.results,
            self.automatic_threshold,
        )

        result = exact_match.process()
        expected_result = []

        self.assertEqual(result, expected_result)
        self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)

    @patch('app.database.models.facility.Facility')
    def test_process_with_one_match(self, facility_mock):
        facility_mock.query().filter().scalar.return_value = False

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

    @patch('app.database.models.facility.Facility')
    def test_process_with_multiple_matches(self, facility_mock):
        facility_mock.query().filter().scalar.return_value = False

        exact_match = ExactItemMatch(
            self.item_id,
            self.matches_multiple,
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
                'results': {'match_type': 'multiple_exact_matches'},
                'confidence': 1,
            }
        ]

        self.assertEqual(result, expected_result)
        self.assertEqual(exact_match.item.status, FacilityListItemTemp.MATCHED)


if __name__ == '__main__':
    unittest.main()
