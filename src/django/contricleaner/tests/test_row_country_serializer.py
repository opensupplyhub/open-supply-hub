from contricleaner.lib.serializers.row_serializers.row_country_serializer \
    import RowCountrySerializer

from django.test import TestCase


class RowCountrySerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowCountrySerializer()
        self.valid_row = {"country": "United States"}
        self.invalid_row = {"country": "Invalid Country"}
        self.current = {"errors": []}

    def test_validate_valid_country(self):
        result = self.serializer.validate(self.valid_row, self.current.copy())

        self.assertIn("country_code", result)
        self.assertEqual(result["country_code"], "US")

    def test_validate_invalid_country(self):
        result = self.serializer.validate(
            self.invalid_row, self.current.copy()
        )

        self.assertIn("errors", result)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["type"], "Error")
        self.assertEqual(
            result["errors"][0]["message"],
            "Could not find a country code for 'Invalid Country'.",
        )
        self.assertEqual(
            result["errors"][0]["field"],
            "country",
        )
        self.assertNotIn("country_code", result)
