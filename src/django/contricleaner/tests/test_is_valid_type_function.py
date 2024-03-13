from contricleaner.lib.helpers.is_valid_type import is_valid_type

from django.test import TestCase


class IsValidTypeFunctionTest(TestCase):
    def test_is_valid_type(self):
        # Test cases for is_valid_type function
        self.assertTrue(is_valid_type("valid_string"))
        self.assertTrue(is_valid_type(["valid", "list"]))
        self.assertFalse(is_valid_type(123))
        self.assertFalse(is_valid_type(["valid", 123]))
