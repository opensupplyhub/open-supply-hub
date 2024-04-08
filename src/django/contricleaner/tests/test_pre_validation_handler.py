import unittest

from contricleaner.lib.handlers.pre_validation_handler \
    import PreValidationHandler
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError


class PreValidationHandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler_one = PreValidationHandler()
        self.handler_two = PreValidationHandler()

    def test_pre_validation_handler(self):
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
        except HandlerNotSetError as exc:
            self.assertEqual("Next Handler wasn't set.", exc.args[0])
