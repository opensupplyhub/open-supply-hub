from contricleaner.lib.serializers.row_serializers.row_clean_field_serializer \
    import RowCleanFieldSerializer

from django.test import TestCase


class RowCleanFieldSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowCleanFieldSerializer("field", "new_field")
        self.valid_row = {"field": "valid value"}
        self.empty_row = {"field": " "}
        self.current = {"errors": []}

    def test_validate_valid_value(self):
        result = self.serializer.validate(self.valid_row, self.current.copy())

        self.assertEqual(result["new_field"], "valid value")

    def test_validate_empty_value(self):
        result = self.serializer.validate(self.empty_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "field cannot consist solely of punctuation or whitespace."
        )
        self.assertEqual(result["errors"][0]["type"], "Error")
        self.assertEqual(result["errors"][0]["field"], "field")
        self.assertNotIn("new_field", result)
