from contricleaner.lib.serializers.row_serializers.row_sector_serializer \
    import RowSectorSerializer
from contricleaner.tests.mockSectorCache import MockSectorCache

from django.test import TestCase


class RowSectorSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowSectorSerializer(MockSectorCache())

        self.row_one = {
            "sector": ['Apparel', 'Finance'],
            "product_type": 'product one',
            "sector_product_type":
                [
                    "Apparel, Finance",
                    "Agriculture, product one, product two, product three",
                    "Agriculture"
                ]
            }
        self.row_two = {"sector": ['Apparel', 'product one']}
        self.current = {"errors": []}

    def test_validate_with_multiple_values(self):
        result = self.serializer.validate(self.row_one, self.current.copy())

        self.assertEqual(
            result['product_type'],
            ['product one', 'product three', 'product two']
        )
        self.assertEqual(
            result['sector'], ['Agriculture', 'Apparel', 'Finance']
        )

    def test_validate_with_single_sector(self):
        result = self.serializer.validate(self.row_two, self.current.copy())

        self.assertEqual(result['product_type'], ['product one'])
        self.assertEqual(result['sector'], ['Apparel'])

    def test_parse_all_values(self):
        all_values = ['technology', 'product one', 'finance']
        sectors, product_types = self.serializer.parse_all_values(all_values)
        self.assertEqual(sectors, ['Finance', 'Technology'])
        self.assertEqual(product_types, ['product one'])

    def test_parse_all_values_no_sectors(self):
        all_values = ['product one', 'product two']
        sectors, product_types = self.serializer.parse_all_values(all_values)
        self.assertEqual(sectors, ['Unspecified'])
        self.assertEqual(product_types, ['product one', 'product two'])

    def test_clean_value(self):
        value = '   Technology  '
        cleaned_value = self.serializer.clean_value(value)
        self.assertEqual(cleaned_value, 'technology')
