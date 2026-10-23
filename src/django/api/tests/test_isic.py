from django.test import SimpleTestCase

from api.isic import parse_isic4_filter_values


class ParseIsic4FilterValuesTest(SimpleTestCase):
    def test_parse_isic4_filter_values(self):
        self.assertEqual(
            parse_isic4_filter_values(['section:C', 'class:0111', 'invalid']),
            [
                ('isic_section', 'C'),
                ('isic_class', '0111'),
            ],
        )
