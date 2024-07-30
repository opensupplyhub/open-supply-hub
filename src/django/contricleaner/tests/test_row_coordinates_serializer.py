from contricleaner.lib.serializers.row_serializers.row_coordinates_serializer \
    import RowCoordinatesSerializer

from django.test import TestCase


class RowCoordinatesSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowCoordinatesSerializer()
        self.current = {
            "country": "United States",
            "name": "Company Name",
            "address": "1234 Main St",
            "errors": [],
        }

    def test_valid_coordinates(self):
        row = {'lat': '40.7128', 'lng': '-74.0060'}
        result = self.serializer.validate(row, self.current)
        self.assertEqual(result['lat'], 40.7128)
        self.assertEqual(result['lng'], -74.0060)

    def test_empty_coordinates(self):
        row = {'lat': '', 'lng': ''}
        result = self.serializer.validate(row, self.current)
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lng'])

    def test_invalid_lat(self):
        row = {'lat': 'invalid', 'lng': '-74.0060'}
        result = self.serializer.validate(row, self.current)
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lng'])

    def test_invalid_lng(self):
        row = {'lat': '40.7128', 'lng': 'invalid'}
        result = self.serializer.validate(row, self.current)
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lng'])

    def test_both_missing(self):
        row = {}
        result = self.serializer.validate(row, self.current)
        self.assertEqual(result, self.current)

    def test_out_of_range_coordinates(self):
        row = {'lat': '91', 'lng': '-181'}
        result = self.serializer.validate(row, self.current)
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lng'])
