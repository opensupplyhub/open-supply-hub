import unittest
from unittest.mock import patch, MagicMock
from api.services.opensearch.search import \
    OpenSearchService, OpenSearchServiceException


class TestPrepareOpenSearchResponse(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = OpenSearchService(client=self.mock_client)

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_valid_response(self, mock_logger):
        response = {
            "hits": {
                "total": {"value": 10},
                "hits": [
                    {"_source": {"field1": "value1"}},
                    {"_source": {"field2": "value2"}}
                ]
            }
        }
        expected_result = {
            "count": 10,
            "data": [
                {"field1": "value1"},
                {"field2": "value2"}
            ]
        }

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_with_varied_null_cases(
        self, mock_logger
    ):
        response = {
            "hits": {
                "total": {"value": 10},
                "hits": [
                    {"_source": {"field1": {
                        "os_id": "CN2024216VGFN6R",
                        "claim_id": 123,
                        "moderation_id":
                            "1f35a90f-70a0-4c3e-8e06-2ed8e1fc6801",
                        "nested_field": {
                            "key1": None,
                            "key2": "valid_value"
                        }
                    }}},
                    {"_source": {
                        "field2": {
                            "os_id": None,
                            "claim_id": None,
                            "moderation_id":
                                "1f35a90f-70a0-4c3e-8e06-2ed8e1fc6817"
                        }
                    }},
                    {"_source": {
                        "field3": {
                            "os_id": "TW2024336G2W87T",
                            "claim_id": None,
                            "moderation_id":
                                "1f35a90f-70a0-4c3e-8e06-2ed8e1fc67ee",
                            "empty_field": None
                        }
                    }},
                    {"other_field": "irrelevant"}
                ]
            }
        }
        expected_result = {
            "count": 10,
            "data": [
                {"field1": {
                    "os_id": "CN2024216VGFN6R",
                    "claim_id": 123,
                    "moderation_id":
                        "1f35a90f-70a0-4c3e-8e06-2ed8e1fc6801",
                    "nested_field": {
                        "key2": "valid_value"
                    }
                }},
                {"field2": {
                    "moderation_id":
                        "1f35a90f-70a0-4c3e-8e06-2ed8e1fc6817"
                }},
                {"field3": {
                    "os_id": "TW2024336G2W87T",
                    "moderation_id":
                        "1f35a90f-70a0-4c3e-8e06-2ed8e1fc67ee"
                }}
            ]
        }

        result = self.service \
            ._OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_called_once_with(
            "Missing '_source' in hit: {'other_field': 'irrelevant'}"
        )

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_missing_source(self, mock_logger):
        response = {
            "hits": {
                "total": {"value": 10},
                "hits": [
                    {"_source": {"field1": "value1"}},
                    {"other_field": {"field2": "value2"}}
                ]
            }
        }
        expected_result = {
            "count": 10,
            "data": [
                {"field1": "value1"}
            ]
        }

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_called_once_with(
            "Missing '_source' in hit: {'other_field': {'field2': 'value2'}}"
        )

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_no_hits(self, mock_logger):
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        expected_result = {"count": 0, "data": []}

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_invalid_response_format(
        self,
        mock_logger
    ):
        response = {}
        with self.assertRaises(OpenSearchServiceException):
            self.service. \
                _OpenSearchService__prepare_opensearch_response(response)
        mock_logger.error.assert_called_once_with(
            "Invalid response format: {}"
            )

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_none_response(
        self,
        mock_logger
    ):
        with self.assertRaises(OpenSearchServiceException):
            self.service. \
                _OpenSearchService__prepare_opensearch_response(None)
        mock_logger.error.assert_called_once_with(
            "Invalid response format: None")

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_rename_lon_field(self, mock_logger):
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {"_source": {"coordinates":
                                 {"lat": 33.44029, "lon": 119.82232}}
                     }
                ]
            }
        }
        expected_result = {
          "count": 1,
          "data": [
            {"coordinates":
             {"lat": 33.44029, "lng": 119.82232}}
          ]
        }

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()

    @patch('api.services.opensearch.search.logger')
    def test_prepare_opensearch_response_with_aggregation_data(
        self,
        mock_logger
    ):
        response = {
            "hits": {
                "total": {"value": 10},
                "hits": [
                    {"_source": {"field1": "value1"}},
                    {"_source": {"field2": "value2"}}
                ]
            },
            "aggregations": {
                "grouped": {
                    "buckets": [
                        {"key": "value1"},
                        {"key": "value2"}
                    ]
                }
            }
        }
        expected_result = {
            "count": 10,
            "data": [
                {"field1": "value1"},
                {"field2": "value2"}
            ],
            "aggregations": {
                "geohex_grid": [
                    {"key": "value1"},
                    {"key": "value2"}
                ]
            }
        }

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()

    @patch('api.services.opensearch.search.logger')
    def test_preserves_geocode_fields(self, mock_logger):
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "os_id": "CN2021250D1DTN7",
                            "name": "location1",
                            "geocoded_location_type": "ROOFTOP",
                            "geocoded_address": "123 Main St, City, Country",
                            "coordinates": {"lat": 10.0, "lon": 20.0},
                        }
                    }
                ]
            }
        }
        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result.get("count"), 1)
        item = result.get("data")[0]
        self.assertEqual(item.get("geocoded_location_type"), "ROOFTOP")
        self.assertEqual(
            item.get("geocoded_address"), "123 Main St, City, Country"
        )
        self.assertEqual(item.get("coordinates", {}).get("lng"), 20.0)


if __name__ == '__main__':
    unittest.main()
