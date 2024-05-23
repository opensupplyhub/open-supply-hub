import unittest
from unittest.mock import MagicMock
from app.matching.matcher.cumulative_matcher import CumulativeMatcher


class TestCumulativeMatcher(unittest.TestCase):
    def setUp(self):
        self.messy = {
            "1": {
                "name": "Test 1",
                "address": "Test 1",
                "country": "Test 1"
            },
            "2": {
                "name": "Test 2",
                "address": "Test 2",
                "country": "Test 2"
            }
        }

        self.processed_matches = [
            {
                "facility_id": "CN20241096SFEBA",
                "confidence": 1.0,
                "facility_list_item_id": "1",
                "status": "AUTOMATIC",
                "results": {}
            },
            {
                "facility_id": "CN20241096SFEBA",
                "confidence": 1.0,
                "facility_list_item_id": "2",
                "status": "AUTOMATIC",
                "results": {}
            }
        ]

    def test_process(self):
        c_m = CumulativeMatcher()

        self.messy["3"] = {
                "name": "Test 3",
                "address": "Test 3",
                "country": "Test 3"
            }

        processed_matches_two = [
            {
                "facility_id": "CN20241096SFEBA",
                "confidence": 1.0,
                "facility_list_item_id": "3",
                "status": "AUTOMATIC",
                "results": {}
            },
        ]

        process_unmatched_items_one = [
            {
                "facility_id": "CN20241096SFEBB",
                "confidence": 1.0,
                "facility_list_item_id": "4",
                "status": "AUTOMATIC",
                "results": {}
            },
        ]

        process_matches_mock = MagicMock()
        process_matches_mock.side_effect = [self.processed_matches, processed_matches_two]
        c_m.process_matches = process_matches_mock

        process_unmatched_items_mock = MagicMock()
        process_unmatched_items_mock.side_effect = [process_unmatched_items_one]
        c_m.process_unmatched_items = process_unmatched_items_mock

        update_extended_fields_mock = MagicMock()
        update_extended_fields_mock.return_value = None
        c_m.update_extended_fields = update_extended_fields_mock

        result = c_m.process(self.messy)

        self.assertEqual(len(result), 4)

        for index, f_m_dto in enumerate(result):
            self.assertEqual(f_m_dto["facility_list_item_id"], str(index + 1))

    def test_clean_matched(self):
        c_m = CumulativeMatcher()

        result_one = c_m.clean_matched(self.messy, self.processed_matches)
        self.assertDictEqual(result_one, {})

        processed_matches_two = [
            {
                "facility_id": "CN20241096SFEBA",
                "confidence": 1.0,
                "facility_list_item_id": "1",
                "status": "AUTOMATIC",
                "results": {}
            },
        ]
        result_two = c_m.clean_matched(self.messy, processed_matches_two)
        self.assertDictEqual(result_two, {
            "2": {
                "name": "Test 2",
                "address": "Test 2",
                "country": "Test 2"
            }
        })
