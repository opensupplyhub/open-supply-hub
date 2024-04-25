import unittest
from unittest.mock import MagicMock, patch
from app.matching.matcher.exact.exact_item_match import ExactItemMatch


class TestExactItemMatch(unittest.TestCase):
    def setUp(self):
        self.item_id = 1
        self.matches = []
        self.started = "2024-04-25 12:00:00"
        self.finished = "2024-04-25 12:10:00"
        self.results = {}
        self.automatic_threshold = 0.5
        self.exact_item_match = ExactItemMatch(
            item_id=self.item_id,
            matches=self.matches,
            started=self.started,
            finished=self.finished,
            results=self.results,
            automatic_threshold=self.automatic_threshold,
        )

    def test_process_no_matches(self):
        item_mock = MagicMock()
        item_mock.id = self.item_id
        item_mock.source_id = 1
        item_mock.status = "UNMATCHED"
        item_mock.facility_id = None

        self.exact_item_match.item = item_mock

        result = self.exact_item_match.process()
        self.assertEqual(result, [])

    # def test_process_single_match(self):
    #     self.exact_item_match.matches = [
    #         {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
    #     ]

    #     with patch.object(
    #         ExactItemMatch, "item_save"
    #     ) as mock_item_save, patch(
    #         "app.matching.matcher.exact.exact_item_match.get_session"
    #     ) as mock_get_session:
    #         mock_session = MagicMock()
    #         mock_get_session.return_value.__enter__.return_value = mock_session
    #         mock_session.query().filter().scalar.return_value = True

    #         result = self.exact_item_match.process()

    #         self.assertEqual(len(result), 1)
    #         self.assertEqual(result[0]["status"], "AUTOMATIC")
    #         self.assertEqual(
    #             result[0]["results"]["match_type"], "single_exact_match"
    #         )
    #         mock_item_save.assert_called_once_with(exact_match=True)

    # @patch("app.matching.matcher.exact.exact_item_match.get_session")
    # def test_process_multiple_matches(self, mock_get_session):
    #     self.exact_item_match.matches = [
    #         {"id": 2072, "facility_id": "CN20241096SFEBA", "score": "1"},
    #         {"id": 2073, "facility_id": "CN20241096SFEBA", "score": "1"},
    #         {"id": 2074, "facility_id": "CN20241096SFEBA", "score": "1"},
    #     ]
    #     with patch.object(
    #         ExactItemMatch, "item_save"
    #     ) as mock_item_save, patch(
    #         "app.matching.matcher.exact.exact_item_match.get_session"
    #     ) as mock_get_session:
    #         mock_session = MagicMock()
    #         mock_get_session.return_value.__enter__.return_value = mock_session
    #         mock_session.query().filter().scalar.return_value = True

    #         result = self.exact_item_match.process()

    #         self.assertEqual(len(result), 1)
    #         self.assertEqual(result[0]["status"], "AUTOMATIC")
    #         self.assertEqual(
    #             result[0]["results"]["match_type"], "multiple_exact_matches"
    #         )
    #         mock_item_save.assert_called_once_with(exact_match=True)


if __name__ == "__main__":
    unittest.main()
