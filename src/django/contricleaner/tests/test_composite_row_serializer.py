from django.test import TestCase

from contricleaner.lib.serializers.row_serializers.composite_row_serializer \
    import CompositeRowSerializer
from contricleaner.tests.sector_cache_mock import SectorCacheMock
from contricleaner.lib.serializers.row_serializers.row_clean_field_serializer \
    import RowCleanFieldSerializer
from contricleaner.lib.serializers.row_serializers.row_country_serializer \
    import RowCountrySerializer
from contricleaner.lib.serializers.row_serializers.row_empty_serializer \
    import RowEmptySerializer
from contricleaner.lib.serializers.row_serializers.\
    row_facility_type_serializer import RowFacilityTypeSerializer
from contricleaner.lib.serializers.row_serializers.row_sector_serializer \
    import RowSectorSerializer
from contricleaner.lib.serializers.row_serializers \
    .row_required_fields_serializer \
    import RowRequiredFieldsSerializer


class CompositeRowSerializerTest(TestCase):
    def setUp(self):
        self.composite_row_serializer = CompositeRowSerializer()
        split_pattern = r', |,|\|'
        leaf_serializers = (
            RowCleanFieldSerializer('name', 'clean_name'),
            RowCleanFieldSerializer('address', 'clean_address'),
            RowSectorSerializer(SectorCacheMock(), split_pattern),
            RowCountrySerializer(),
            RowRequiredFieldsSerializer(),
            RowFacilityTypeSerializer(split_pattern),
            RowEmptySerializer(),
        )

        for serializer in leaf_serializers:
            self.composite_row_serializer.add_serializer(serializer)

    def test_get_serialized_row(self):
        facility_source = {
            'country': 'United States',
            'name': 'Pants Hut',
            'address': '123 Main St, Anywhereville, PA',
            'sector': 'Apparel',
            'product_type': 'product one',
            'extra_1': 'Extra data',
            'facility_type': 'Blending|Knitting'
        }

        serialized_row = self.composite_row_serializer \
            .validate(facility_source)

        expected_row = {
            'fields': {
                'product_type': ['product one'],
                'facility_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Knitting', 'Blending'},
                },
                'processing_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Knitting', 'Blending'},
                },
                'country': 'United States',
                'extra_1': 'Extra data',
            },
            'errors': [],
            'clean_name': 'pants hut',
            'clean_address': '123 main st anywhereville pa',
            'sector': ['Apparel'],
            'country_code': 'US',
            'address': '123 Main St, Anywhereville, PA',
            'name': 'Pants Hut',
        }

        self.assertEqual(serialized_row, expected_row)
