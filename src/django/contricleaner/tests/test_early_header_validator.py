import unittest

from contricleaner.lib.validators \
    .early_validators.early_header_validator \
    import EarlyHeaderValidator


class EarlyHeaderValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = EarlyHeaderValidator()
    
    def test_validate_header(self):
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

        res_one = self.validator.validate([facility_source_two, facility_source_one])

        self.assertEqual(res_one, {})

        res_two = self.validator.validate([facility_source_three, facility_source_two])

        self.assertEqual(res_two["type"], "Error")
