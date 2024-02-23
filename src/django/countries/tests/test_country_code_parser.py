from countries.lib.get_country_code import get_country_code

from django.test import TestCase


class CountryCodeParserTest(TestCase):
    def test_parse_countries_with_new_lines(self):
        self.assertEqual(get_country_code("United\nKingdom"), "GB")
        self.assertEqual(get_country_code("Dominican\r\nRepublic"), "DO")
        self.assertEqual(get_country_code("Russian\n\nFederation"), "RU")
        self.assertEqual(get_country_code("Hong\r\n\r\nKong"), "HK")

    def test_parse_hong_kong_sar(self):
        self.assertEqual(get_country_code("Hong Kong SAR"), "HK")

    def test_parse_turkiye(self):
        names = ("Türkiye", "Turkiye", "TÜRKİYE", "TURKİYE", "Turkey")
        for name in names:
            self.assertEqual(get_country_code(name), "TR")
