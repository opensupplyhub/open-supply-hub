from contricleaner.lib.serializers.row_serializers.row_sector_serializer import (
    RowSectorSerializer,
)

from django.test import TestCase


class RowSectorSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowSectorSerializer()
        self.row = {"sector": "Apparel,Finance,Healthcare"}
        self.current = {"errors": []}

    def test_validate(self):
        result = self.serializer.validate(self.row, self.current.copy())

        self.assertIn("sector", result)
        self.assertEqual(
            result["sector"], ['Apparel', 'Finance', 'Healthcare']
        )
