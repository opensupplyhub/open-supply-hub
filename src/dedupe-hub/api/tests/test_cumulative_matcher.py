import unittest
from app.matching.matcher.cumulative_matcher import CumulativeMatcher

class TestCumulativeMatcher(unittest.TestCase):

    def test_clean_matched(self):
        c_m = CumulativeMatcher()
        messy = {
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
        processed_matches_one = [
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
        result_one = c_m.clean_matched(messy, processed_matches_one)
        self.assertEqual(result_one, {})

        processed_matches_two = [
            {
                "facility_id": "CN20241096SFEBA",
                "confidence": 1.0,
                "facility_list_item_id": "1",
                "status": "AUTOMATIC",
                "results": {}
            },
        ]
        result_two = c_m.clean_matched(messy, processed_matches_two)
        self.assertEqual(result_two, {
            "2": {
                "name": "Test 2",
                "address": "Test 2",
                "country": "Test 2"
            }
        })