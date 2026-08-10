from django.test import SimpleTestCase

from api.isic import normalize_isic_code, parse_isic4_filter_values


class NormalizeIsicCodeTest(SimpleTestCase):
    def test_extracts_section_code(self):
        self.assertEqual(
            normalize_isic_code('C - Manufacturing'),
            'C',
        )

    def test_extracts_four_digit_class_code(self):
        self.assertEqual(
            normalize_isic_code(
                '0111 - Growing of cereals (except rice), leguminous crops '
                'and oil seeds',
            ),
            '0111',
        )

    def test_extracts_two_digit_division_code(self):
        self.assertEqual(
            normalize_isic_code(
                '62 - Computer programming, consultancy and related activities',
            ),
            '62',
        )

    def test_uppercases_alpha_codes(self):
        self.assertEqual(
            normalize_isic_code('j - Information and communication'),
            'J',
        )

    def test_accepts_bare_numeric_code(self):
        self.assertEqual(normalize_isic_code('620'), '620')

    def test_accepts_bare_alpha_code(self):
        self.assertEqual(normalize_isic_code('a'), 'A')

    def test_returns_none_for_empty_values(self):
        self.assertIsNone(normalize_isic_code(None))
        self.assertIsNone(normalize_isic_code(''))
        self.assertIsNone(normalize_isic_code('   '))

    def test_returns_none_for_unrecognized_strings(self):
        self.assertIsNone(normalize_isic_code('Manufacturing'))
        self.assertIsNone(normalize_isic_code('not-a-code'))

    def test_parse_isic4_filter_values(self):
        self.assertEqual(
            parse_isic4_filter_values(['section:C', 'class:0111', 'invalid']),
            [
                ('isic_section', 'C'),
                ('isic_class', '0111'),
            ],
        )
