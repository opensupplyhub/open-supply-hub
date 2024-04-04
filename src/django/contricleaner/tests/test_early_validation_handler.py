import unittest

from contricleaner.lib.handlers.early_validation_handler \
    import EarlyValidationHandler


class EarlyValidationHandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler = EarlyValidationHandler()
    
    def test_early_validation_handler(self):
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

        list_dto = self.handler.handle([facility_source_three, facility_source_two])

        self.assertEqual(len(list_dto.errors), 1)

        try:
            self.handler.handle([facility_source_one, facility_source_two])
        except KeyError as ke:
            self.assertEqual("Next Handler wasn't set", ke.args[0])
