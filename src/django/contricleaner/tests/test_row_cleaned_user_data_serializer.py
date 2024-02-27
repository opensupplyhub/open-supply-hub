from contricleaner.lib.serializers.row_serializers.\
    row_cleaned_user_data_serializer import RowCleanedUserDataSerializer

from django.test import TestCase


class RowCleanedUserDataSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowCleanedUserDataSerializer()
        self.row = {"name": "Company Name", "address": "1234 Main St",}
        self.current = {"errors": []}

    def test_validate(self):
        result = self.serializer.validate(self.row, self.current.copy())
        self.assertIn("cleaned_user_data", result)
        self.assertEqual(result["cleaned_user_data"], self.row)
