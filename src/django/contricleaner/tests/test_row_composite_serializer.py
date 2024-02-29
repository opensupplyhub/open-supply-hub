import unittest

from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer


class RowCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_row(self):
        validator = RowCompositeSerializer()
        facility_source = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }
        res = validator.get_validated_row(facility_source)

        expected = RowDTO(
            errors=[],
            name="Pants Hut",
            clean_name="pants hut",
            address="123 Main St, Anywhereville, PA",
            clean_address="123 main st anywhereville pa",
            sector=["Apparel"],
            raw_json=facility_source,
            country_code="US",
            fields={
                'country': 'United States',
                'errors': [],
                'extra_1': 'Extra data'
            },
        )
        self.assertRowEqual(res, expected)

    def assertRowEqual(self, res, expected):
        self.assertEqual(res.errors, expected.errors)
        self.assertEqual(res.name, expected.name)
        self.assertEqual(res.clean_name, expected.clean_name)
        self.assertEqual(res.address, expected.address)
        self.assertEqual(res.clean_address, expected.clean_address)
        self.assertEqual(res.sector, expected.sector)
        self.assertEqual(res.raw_json, expected.raw_json)
        self.assertEqual(res.country_code, expected.country_code)
        self.assertEqual(res.fields, expected.fields)
