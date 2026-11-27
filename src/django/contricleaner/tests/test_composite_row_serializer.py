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
            'facility_type': 'Knitting'
        }

        serialized_row = self.composite_row_serializer \
            .validate(facility_source)

        expected_row = {
            'fields': {
                'product_type': ['product one'],
                'facility_type': {
                    'raw_values': 'Knitting',
                    'processed_values': ['Knitting'],
                },
                'processing_type': {
                    'raw_values': 'Knitting',
                    'processed_values': ['Knitting'],
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

    def test_row_clean_up(self):
        facility_source_uncleaned = {
            "country": "United \"States\"",
            "name": "Simple, , , Pants,,,Hut",
            "address": "123 \"Main\"\" St,,,Anywhereville, , ,PA",
            "sector": "Apparel",
            "product_type": "product one",
            "extra_1": (
                "extra one,, , “extra two”,   ,extra three,  \"extra four"
            ),
            "extra_2": "Technology Co., ,Ltd.",
            "extra_3": (
                "Optimum Fashion Manufacturing Co Ltd. "
                "(Former name “United Apparel (Cambodia) Inc. - Head Factory”)"
            ),
            "extra_4": "Mohib Shoes Pvt. Ltd., „B“ Unit",
            "extra_5": "«Global» Manufactoring",
            "extra_6": "‹NanoTech› Technologies",
            'extra_7': "Nantong, Jackbeanie,, Headwear! & Garment Co. Ltd.",
            "extra_8": "\"Baker Street 221B.   , this is a test\"",
            "facility_type": "Blending"
        }
        serialized_row = self.composite_row_serializer \
            .validate(facility_source_uncleaned)

        expected_row = {
            "fields": {
                "product_type": ["product one"],
                "facility_type": {
                    "raw_values": "Blending",
                    "processed_values": ["Blending"],
                },
                "processing_type": {
                    "raw_values": "Blending",
                    "processed_values": ["Blending"],
                },
                "extra_5": "Global Manufactoring",
                "country": "United States",
                "extra_6": "NanoTech Technologies",
                "extra_3": ("Optimum Fashion Manufacturing Co Ltd. "
                            "(Former name United Apparel (Cambodia) Inc. - "
                            "Head Factory)"),
                "extra_8": "Baker Street 221B., this is a test",
                "extra_2": "Technology Co., Ltd.",
                "extra_7": "Nantong, Jackbeanie, Headwear! & Garment Co. Ltd.",
                "extra_1": "extra one, extra two, extra three, extra four",
                "extra_4": "Mohib Shoes Pvt. Ltd., B Unit",
            },
            "errors": [],
            "clean_name": "simple pants hut",
            "clean_address": "123 main st anywhereville pa",
            "sector": ["Apparel"],
            "country_code": "US",
            "address": "123 Main St, Anywhereville, PA",
            "name": "Simple, Pants, Hut",
        }

        self.assertEqual(serialized_row, expected_row)

    @staticmethod
    def __build_value(prefix: str, length: int) -> str:
        # Commas without a following space: cleanup adds one after each.
        value = prefix + ',Block A,Unit 7'
        return value + 'x' * (length - len(value))

    def __length_errors(self, serialized_row):
        return [
            error for error in serialized_row['errors']
            if error['type'] == 'ValidationError'
        ]

    def test_length_limit_checks_submitted_value_not_cleaned(self):
        name = self.__build_value('Pants Hut', 200)
        address = self.__build_value('123 Main St', 200)

        serialized_row = self.composite_row_serializer.validate({
            'country': 'United States',
            'name': name,
            'address': address,
            'sector': 'Apparel',
        })

        self.assertEqual(self.__length_errors(serialized_row), [])
        # The stored values are still the cleaned ones, which are longer
        # than what was submitted.
        self.assertEqual(serialized_row['name'], name.replace(',', ', '))
        self.assertEqual(
            serialized_row['address'], address.replace(',', ', ')
        )
        self.assertEqual(len(serialized_row['name']), 202)
        self.assertEqual(len(serialized_row['address']), 202)

    def test_length_limit_rejects_submitted_value_over_limit(self):
        serialized_row = self.composite_row_serializer.validate({
            'country': 'United States',
            'name': self.__build_value('Pants Hut', 201),
            'address': self.__build_value('123 Main St', 201),
            'sector': 'Apparel',
        })

        self.assertEqual(
            self.__length_errors(serialized_row),
            [
                {
                    'message': ('There is a problem with the name: Ensure '
                                'this value has at most 200 characters. '
                                '(it has 201)'),
                    'field': 'name',
                    'type': 'ValidationError',
                },
                {
                    'message': ('There is a problem with the address: Ensure '
                                'this value has at most 200 characters. '
                                '(it has 201)'),
                    'field': 'address',
                    'type': 'ValidationError',
                },
            ],
        )

    def test_length_limit_rejects_over_limit_value_cleanup_shortens(self):
        # Cleanup collapses the repeated spaces to a value under the limit,
        # but the limit applies to what the contributor submitted.
        address = '123 Main St' + ' ' * 100 + 'x' * 100

        serialized_row = self.composite_row_serializer.validate({
            'country': 'United States',
            'name': 'Pants Hut',
            'address': address,
            'sector': 'Apparel',
        })

        self.assertEqual(len(serialized_row['address']), 112)
        self.assertEqual(
            [e['field'] for e in self.__length_errors(serialized_row)],
            ['address'],
        )
