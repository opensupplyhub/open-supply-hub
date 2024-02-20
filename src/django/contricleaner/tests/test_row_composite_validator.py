import unittest

from contricleaner.lib.row_validators.row_composite_validator import (
    RowCompositeValidator,
)
from contricleaner.lib.dto.row_dto import RowDTO


class RowCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_row(self):
        validator = RowCompositeValidator()
        faciliry_source = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }
        res = validator.get_validated_row(faciliry_source)
        
        expected = RowDTO(
            errors=[],
            name="Pants Hut",
            clean_name="pants hut",
            address="123 Main St, Anywhereville, PA",
            clean_address="123 main st anywhereville pa",
            sector=["Apparel"],
            raw_json=faciliry_source,
            country_code="US",
            fields={},
        )
        self.assertRowEqual(res, expected)

    def assertRowEqual(self, res, expected):
        
        print(">>>> res: {}".format(res))
        print(">>>> expected: {}".format(expected))

        self.assertEqual(res.errors, expected.errors)
        self.assertEqual(res.name, expected.name)
        self.assertEqual(res.clean_name, expected.clean_name)
        self.assertEqual(res.address, expected.address)
        self.assertEqual(res.clean_address, expected.clean_address)
        self.assertEqual(res.sector, expected.sector)
        self.assertEqual(res.raw_json, expected.raw_json)
        self.assertEqual(res.country_code, expected.country_code)
        # self.assertEqual(res.fields, expected.fields)


    def test_get_missing_reuired_fields(self):
        validator = RowCompositeValidator()
        res = validator.get_validated_row(
            {
                "country": "United States",
                # "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
                "sector": "Apparel",
                "extra_1": "Extra data",
            }
        )
        self.assertEqual(res.errors, [])
        self.assertEqual(res.name, "")
        self.assertEqual(res.clean_name, "")
        self.assertEqual(res.address, "test")
        self.assertEqual(res.clean_address, "test")
        self.assertEqual(res.sector, "test")
        self.assertEqual(res.errors, [])
