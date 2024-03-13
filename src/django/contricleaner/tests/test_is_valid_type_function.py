from contricleaner.lib.helpers.is_invalid_type import is_invalid_type

from django.test import TestCase


class IsInvalidTypeFunctionTest(TestCase):
    def test_is_invalid_type(self):
        # Test cases for is_invalid_type function
        self.assertFalse(is_invalid_type("valid_string"))
        self.assertFalse(is_invalid_type(["valid", "list"]))
        self.assertTrue(is_invalid_type(123))
        self.assertTrue(is_invalid_type(["valid", 123]))
