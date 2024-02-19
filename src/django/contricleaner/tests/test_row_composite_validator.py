
import unittest

from contricleaner.lib.row_validators.row_composite_validator import (
    RowCompositeValidator
)


class RowCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_row(self):
        validator = RowCompositeValidator()
        res = validator.get_validated_row(
            {
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
                "sector": "Apparel",
                "extra_1": "Extra data",
            }
        )
        self.assertEqual(res.errors, [])
        self.assertEqual(res.name, 'test')
        self.assertEqual(res.clean_name, 'test')
        self.assertEqual(res.address, 'test')
        self.assertEqual(res.clean_address, 'test')
        self.assertEqual(res.sector, 'test')
        self.assertEqual(res.sector, 'test')
        self.assertEqual(res.errors, [])

        