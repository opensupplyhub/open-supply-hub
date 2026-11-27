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

        result = c_m.process(self.messy)

        self.assertEqual(len(result), 4)

        for index, f_m_dto in enumerate(result):
            self.assertEqual(f_m_dto["facility_list_item_id"], str(index + 1))

    def test_process_matches_stages_item_updates(self):
        """
        Item statuses are collected for the Writer instead of being written
        by the item matchers (OSDEV-3149).
        """
        c_m = CumulativeMatcher()
        update = {
            "facility_list_item_id": 1,
            "source_id": 1,
            "status": "MATCHED",
            "facility_id": "CN20241096SFEBA",
            "processing_results": [],
            "new_facility": None,
        }
        item_match = MagicMock()
        item_match.process.return_value = [self.processed_matches[0]]
        item_match.pending_item_update = update
        matcher = MagicMock()
        matcher.process.return_value = {"1": [{"id": "1"}]}
        matcher.item_match.return_value = item_match

        result = c_m.process_matches(matcher, {"1": self.messy["1"]})

        self.assertEqual(result, [self.processed_matches[0]])
        self.assertDictEqual(c_m.item_updates, {1: update})

    def test_process_matches_without_staged_update(self):
        c_m = CumulativeMatcher()
        item_match = MagicMock()
        item_match.process.return_value = []
        item_match.pending_item_update = None
        matcher = MagicMock()
        matcher.process.return_value = {"1": []}
        matcher.item_match.return_value = item_match

        self.assertEqual(c_m.process_matches(matcher, self.messy), [])
        self.assertDictEqual(c_m.item_updates, {})

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
