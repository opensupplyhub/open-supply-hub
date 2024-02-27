from contricleaner.lib.serializers.row_serializers.row_empty_serializer import (
    RowEmptySerializer,
)

from django.test import TestCase


class RowEmptySerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowEmptySerializer()
        self.current = {
            "errors": [],
            "name": "Company Name",
            "address": "1234 Main St",
        }
        self.new_fields_row = {
            "name": "Company Name",
            "address": "1234 Main St",
            'country': 'United States',
        }

    def test_validate_new_fields(self):
        result = self.serializer.validate(
            self.new_fields_row, self.current.copy()
        )
        expected_result = {
            'errors': [],
            'name': 'Company Name',
            'address': '1234 Main St',
            'country': 'United States',
        }

        self.assertEqual(result, expected_result)
