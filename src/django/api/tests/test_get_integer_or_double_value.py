from django.test import SimpleTestCase

from api.extended_fields import get_integer_or_double_value


class GetIntegerOrDoubleValueTest(SimpleTestCase):
    """
    Numeric data-center values (see DATA_CENTER_NUMERICAL_FIELDS) are
    normalised before being stored in the ExtendedField value JSON.
    """

    def test_whole_numbers_return_ints(self):
        self.assertEqual(get_integer_or_double_value(20), 20)
        self.assertEqual(get_integer_or_double_value('20'), 20)
        self.assertEqual(get_integer_or_double_value(20.0), 20)
        self.assertEqual(get_integer_or_double_value('20.0'), 20)

    def test_fractional_strings_keep_their_precision(self):
        self.assertEqual(get_integer_or_double_value('1.25'), 1.25)
        self.assertEqual(get_integer_or_double_value('2.5'), 2.5)

    def test_native_floats_are_not_truncated(self):
        # int() truncates float input without raising, so a PUE of 1.2
        # arriving as a native float must not be stored as 1.
        self.assertEqual(get_integer_or_double_value(1.2), 1.2)
        self.assertEqual(get_integer_or_double_value(1.8), 1.8)

    def test_negative_and_zero_values(self):
        self.assertEqual(get_integer_or_double_value(0), 0)
        self.assertEqual(get_integer_or_double_value('-3.5'), -3.5)

    def test_non_numeric_values_return_strings(self):
        self.assertEqual(get_integer_or_double_value('about 20'), 'about 20')
        self.assertEqual(get_integer_or_double_value(''), '')
        self.assertEqual(get_integer_or_double_value(None), 'None')

    def test_booleans_are_not_treated_as_numbers(self):
        self.assertEqual(get_integer_or_double_value(True), 'True')
        self.assertEqual(get_integer_or_double_value(False), 'False')

    def test_non_finite_values_are_not_stored_as_numbers(self):
        # NaN and Infinity are not valid JSON.
        self.assertEqual(get_integer_or_double_value(float('nan')), 'nan')
        self.assertEqual(get_integer_or_double_value('NaN'), 'NaN')
        self.assertEqual(get_integer_or_double_value(float('inf')), 'inf')
