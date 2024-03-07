from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.tests.mockSectorCache import MockSectorCache

from django.test import TestCase


class RowCompositeValidatorTest(TestCase):
    def setUp(self):
        self.serializer = RowCompositeSerializer(MockSectorCache())

    def test_get_validated_row(self):
        facility_source = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "product_type": "product one",
            "extra_1": "Extra data",
            "facility_type": "Blending|Knitting"
        }
        validated_row = self.serializer.get_validated_row(facility_source)

        expected_row = RowDTO(
            raw_json=facility_source,
            name='Pants Hut',
            clean_name='pants hut',
            address='123 Main St, Anywhereville, PA',
            clean_address='123 main st anywhereville pa',
            country_code='US',
            sector='Apparel',
            fields={
                'errors': [],
                'product_types': ['product one'],
                'sectors': ['Apparel'],
                'country': 'United States',
                'product_type': 'product one',
                'extra_1': 'Extra data',
                'facility_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Blending', 'Knitting'}
                },
                'processing_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Blending', 'Knitting'}
                }
            },
            errors=[]
        )

        self.assertRowEqual(validated_row, expected_row)

    def assertRowEqual(self, validated_row, expected):
        self.assertEqual(validated_row.errors, expected.errors)
        self.assertEqual(validated_row.name, expected.name)
        self.assertEqual(validated_row.clean_name, expected.clean_name)
        self.assertEqual(validated_row.address, expected.address)
        self.assertEqual(validated_row.clean_address, expected.clean_address)
        self.assertEqual(validated_row.sector, expected.sector)
        self.assertEqual(validated_row.raw_json, expected.raw_json)
        self.assertEqual(validated_row.country_code, expected.country_code)
        self.assertEqual(validated_row.fields, expected.fields)
