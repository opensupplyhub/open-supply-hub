from api.geocoding import create_geocoding_params, format_geocoded_address_data
from api.tests.test_data import parsed_city_hall_data

from django.conf import settings
from django.test import TestCase


class GeocodingUtilsTest(TestCase):
    def setUp(self):
        settings.GOOGLE_SERVER_SIDE_API_KEY = "world"

    def test_geocoding_params_are_created_correctly(self):
        self.assertEqual(
            create_geocoding_params("hello", "US"),
            {
                "components": "country:US",
                "address": "hello",
                "key": "world",
            },
        )

    def test_geocoded_address_data_is_formatted_correctly(self):
        data = parsed_city_hall_data["full_response"]
        formatted_data = format_geocoded_address_data(data, data["results"][0])
        self.assertEqual(formatted_data, parsed_city_hall_data)
