from unittest.mock import Mock, patch

from api.geocoding import geocode_address
from api.tests.test_data import (
    geocoding_data,
    geocoding_data_no_country,
    geocoding_data_second_country,
)

from django.test import TestCase


class GeocodingTest(TestCase):
    @patch("api.geocoding.requests.get")
    def test_geocode_response_contains_expected_keys(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        geocoded_data = geocode_address("990 Spring Garden St, Philly", "US")
        self.assertIn("full_response", geocoded_data)
        self.assertIn("geocoded_address", geocoded_data)
        self.assertIn("geocoded_point", geocoded_data)
        self.assertIn("lat", geocoded_data["geocoded_point"])
        self.assertIn("lng", geocoded_data["geocoded_point"])

    @patch("api.geocoding.requests.get")
    def test_ungeocodable_address_returns_zero_resusts(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = {
            "results": [],
            "status": "ZERO_RESULTS",
        }
        results = geocode_address("@#$^@#$^", "XX")
        self.assertEqual(0, results["result_count"])

    @patch("api.geocoding.requests.get")
    def test_incorrect_country_code_raises_error(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        with self.assertRaises(ValueError) as cm:
            geocode_address(
                "Datong Bridge, Qiucun town, Fenghua District, "
                + "Tirupur, Tamilnadu, 641604",
                "IN",
            )

        self.assertEqual(
            cm.exception.args,
            (
                "Geocoding results of US did not match "
                + "provided country code of IN.",
            ),
        )

    @patch("api.geocoding.requests.get")
    def test_accepts_inexact_address(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data_no_country

        expected_result = geocoding_data_no_country["results"][0]
        expected_point = expected_result["geometry"]["location"]
        expected_address = expected_result["formatted_address"]

        results = geocode_address(
            "PortİSBİ Serbest Bölge Office:4, "
            + "Gazimağusa, North Cyprus, 99450",
            "TR",
        )
        self.assertEqual(expected_point, results["geocoded_point"])
        self.assertEqual(expected_address, results["geocoded_address"])

    @patch("api.geocoding.requests.get")
    def test_accepts_alternate_address(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data_second_country

        expected_result = geocoding_data_second_country["results"][1]
        expected_point = expected_result["geometry"]["location"]
        expected_address = expected_result["formatted_address"]

        results = geocode_address(
            "Noorbagh, Kaliakoir Gazipur Dhaka 1704", "BD"
        )
        self.assertEqual(expected_point, results["geocoded_point"])
        self.assertEqual(expected_address, results["geocoded_address"])

    @patch("api.geocoding.requests.get")
    def test_geocode_non_200_response(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=400)
        with self.assertRaisesRegex(ValueError, "400"):
            geocode_address("Noorbagh, Kaliakoir Gazipur Dhaka 1704", "BD")
