import unittest

from contricleaner.lib.validators \
    .early_validators.composite_early_validator \
    import CompositeEarlyValidator
from contricleaner.lib.validators \
    .early_validators.early_header_validator \
    import EarlyHeaderValidator


class CompositeEarlyValidatorTest(unittest.TestCase):

    def setUp(self):
        self.composite = CompositeEarlyValidator()
        self.composite.add_validator(EarlyHeaderValidator())
    
    def test_composite_early_validator(self):
        facility_source_one = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

        facility_source_two = {
            "country": "United States",
            "name": "Pants Hut",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

        facility_source_three = {
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

        res_one = self.composite.validate([facility_source_two, facility_source_one])

        self.assertEqual(len(res_one["errors"]), 0)

        res_two = self.composite.validate([facility_source_three, facility_source_two])

        self.assertEqual(len(res_two["errors"]), 1)
