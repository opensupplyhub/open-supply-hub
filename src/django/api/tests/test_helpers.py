from django.test import TestCase
from api.helpers.helpers import cleanup_data


class CleanupDataTestCase(TestCase):

    def test_multiple_commas(self):
        self.assertEqual(cleanup_data("text1,,text2"), "text1, text2")

    def test_spaces_and_commas(self):
        self.assertEqual(cleanup_data("text1, ,text2"), "text1, text2")

    def test_trailing_commas_and_spaces(self):
        self.assertEqual(cleanup_data("text1, text2, "), "text1, text2")

    def test_no_change_required(self):
        self.assertEqual(cleanup_data("text1, text2"), "text1, text2")

    def test_complex_string(self):
        self.assertEqual(
            cleanup_data(
                "text1,,text2, , ,text3, , text4 text5, text6 text7,, , text8"
            ),
            "text1, text2, text3, text4 text5, text6 text7, text8"
        )
