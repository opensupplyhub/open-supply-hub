import unittest

from contricleaner.lib.handlers.early_validation_handler \
    import EarlyValidationHandler


class EarlyValidationHandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler_one = EarlyValidationHandler()
        self.handler_two = EarlyValidationHandler()

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

        list_dto = self.handler_one.handle(
            [facility_source_three, facility_source_two]
        )

        self.assertNotEqual(len(list_dto.errors), 0)

        try:
            self.handler_two.handle([facility_source_one, facility_source_two])
        except Exception as exc:
            self.assertEqual("Next Handler wasn't set", exc.args[0])
