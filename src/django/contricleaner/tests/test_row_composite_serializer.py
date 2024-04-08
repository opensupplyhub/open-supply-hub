from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.tests.mockSectorCache import MockSectorCache

from django.test import TestCase


class RowCompositeValidatorTest(TestCase):
    def setUp(self):
        self.split_pattern = r', |,|\|'
        self.serializer = RowCompositeSerializer(
            MockSectorCache(), self.split_pattern
        )

    def test_get_validated_row(self):
        facility_source = [{
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "product_type": "product one",
            "extra_1": "Extra data",
            "facility_type": "Blending|Knitting"
        }]

        validated_rows = [self.serializer
                          .get_validated_row(row) for row in facility_source]

        expected_row = RowDTO(
            raw_json=facility_source[0],
            name="Pants Hut",
            clean_name="pants hut",
            address="123 Main St, Anywhereville, PA",
            clean_address="123 main st anywhereville pa",
            country_code="US",
            sector=["Apparel"],
            fields={
                "product_type": ["product one"],
                "country": "United States",
                "extra_1": "Extra data",
                "facility_type": {
                    "raw_values": "Blending|Knitting",
                    "processed_values": {"Blending", "Knitting"}
                },
                "processing_type": {
                    "raw_values": "Blending|Knitting",
                    "processed_values": {"Blending", "Knitting"}
                }
            },
            errors=[]
        )

        self.assertRowEqual(validated_rows[0], expected_row)

    def test_row_clean_up(self):
        facility_source_uncleaned = [{
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
            "facility_type": "Blending|Knitting"
        }]
        validated_rows = [self.serializer
                          .get_validated_row(row) for row in
                          facility_source_uncleaned]
        expected_row = RowDTO(
            raw_json=facility_source_uncleaned[0],
            name="Simple, Pants, Hut",
            clean_name="simple pants hut",
            address="123 Main St, Anywhereville, PA",
            clean_address="123 main st anywhereville pa",
            country_code="US",
            sector=["Apparel"],
            fields={
                "product_type": ["product one"],
                "country": "United States",
                "extra_1": "extra one, extra two, extra three, extra four",
                "extra_2": "Technology Co., Ltd.",
                "extra_3": (
                    "Optimum Fashion Manufacturing Co Ltd. "
                    "(Former name United Apparel "
                    "(Cambodia) Inc. - Head Factory)"
                ),
                "extra_4": "Mohib Shoes Pvt. Ltd., B Unit",
                "extra_5": "Global Manufactoring",
                "extra_6": "NanoTech Technologies",
                'extra_7': "Nantong, Jackbeanie, Headwear! & Garment Co. Ltd.",
                "extra_8": "Baker Street 221B., this is a test",
                "facility_type": {
                    "raw_values": "Blending|Knitting",
                    "processed_values": {"Blending", "Knitting"}
                },
                "processing_type": {
                    "raw_values": "Blending|Knitting",
                    "processed_values": {"Blending", "Knitting"}
                }
            },
            errors=[]
        )
        self.assertRowEqual(validated_rows[0], expected_row)

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
