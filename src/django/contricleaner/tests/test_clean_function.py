from contricleaner.lib.helpers.clean import clean

from django.test import TestCase


class CleanFunctionTest(TestCase):
    def test_clean_function(self):
        test_cases = [
            ("Test string with\nnew line", "test string with new line"),
            ("Test-string with punctuation", "teststring with punctuation"),
            ("Test/with/slashes", "test with slashes"),
            ("'Test' with 'quotes'", "test with quotes"),
            ("Test, with, commas", "test with commas"),
            ("Test:with:colons", "test with colons"),
            (
                " Test  with  excess  whitespace ",
                "test with excess whitespace",
            ),
            ("", None),
            (" ", None),
            ("    ", None),
        ]

        for input_str, expected_output in test_cases:
            self.assertEqual(clean(input_str), expected_output)
