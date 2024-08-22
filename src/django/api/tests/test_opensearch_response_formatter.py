import unittest
from unittest.mock import patch, MagicMock
from api.services.search import \
    OpenSearchService, OpenSearchServiceException


class TestPrepareOpenSearchResponse(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = OpenSearchService(client=self.mock_client)

    @patch('api.services.search.logger')
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

    @patch('api.services.search.logger')
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

    @patch('api.services.search.logger')
    def test_prepare_opensearch_response_no_hits(self, mock_logger):
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        expected_result = {"count": 0, "data": []}

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()

    @patch('api.services.search.logger')
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

    @patch('api.services.search.logger')
    def test_prepare_opensearch_response_none_response(
        self,
        mock_logger
    ):
        with self.assertRaises(OpenSearchServiceException):
            self.service. \
                _OpenSearchService__prepare_opensearch_response(None)
        mock_logger.error.assert_called_once_with(
            "Invalid response format: None")

    @patch('api.services.search.logger')
    def test_prepare_opensearch_response_rename_lon_field(self, mock_logger):
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {"_source": {"coordinates":
                                 {"lon": 119.82232, "lat": 33.44029}}
                     }
                ]
            }
        }
        expected_result = {
          "count": 1,
          "data": [
            {"coordinates":
             {"lng": 119.82232, "lat": 33.44029}}
          ]
        }

        result = self.service. \
            _OpenSearchService__prepare_opensearch_response(response)
        self.assertEqual(result, expected_result)
        mock_logger.warning.assert_not_called()


if __name__ == '__main__':
    unittest.main()
