from contricleaner.lib.serializers.row_serializers.row_sector_serializer \
    import RowSectorSerializer
from contricleaner.tests.sector_cache_mock import SectorCacheMock

from django.test import TestCase


class RowSectorSerializerTest(TestCase):
    def setUp(self):
        self.split_pattern = r', |,|\|'
        self.serializer = RowSectorSerializer(
            SectorCacheMock(), self.split_pattern
        )

        self.row_one = {
            "sector": ['Apparel', 'Finance'],
            "product_type": 'product one',
            "sector_product_type": [
                "Apparel, Finance",
                "Agriculture|product one|product two|product three",
                "Agriculture",
            ],
        }
        self.row_two = {"sector": ['Apparel', 'product one']}
        self.row_three = {"sector": [], "product_type": ''}
        self.row_four = {
            "sector": 1,
            "product_type": 2,
            "sector_product_type": 3,
        }
        self.row_five = {"sector": 'Apparel'}
        self.current = {"errors": []}

    def test_validate_with_multiple_values(self):
        result = self.serializer.validate(self.row_one, self.current.copy())

        self.assertEqual(
            result['product_type'],
            ['product one', 'product three', 'product two'],
        )
        self.assertEqual(
            result['sector'], ['Agriculture', 'Apparel', 'Finance']
        )

    def test_validate_with_single_sector(self):
        result = self.serializer.validate(self.row_two, self.current.copy())

        self.assertEqual(result['product_type'], ['product one'])
        self.assertEqual(result['sector'], ['Apparel'])

    def test_validate_without_product_type_values(self):
        result = self.serializer.validate(self.row_five, self.current.copy())

        self.assertEqual(result['sector'], ['Apparel'])
        self.assertNotIn('product_type', result)

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

    def test_validate_with_empty_values(self):
        result = self.serializer.validate(self.row_three, self.current.copy())
        self.assertEqual(result['errors'], [])

    def test_validate_with_invalid_type(self):
        result = self.serializer.validate(self.row_four, self.current.copy())
        self.assertEqual(
            result['errors'],
            [
                {
                    'message': 'Expected value for sector to be a string or a '
                    'list of strings but got 1.',
                    'field': 'sector',
                    'type': 'ValueError',
                },
                {
                    'message': 'Expected value for product_type to be a '
                    'string or a list of strings but got 2.',
                    'field': 'product_type',
                    'type': 'ValueError',
                },
                {
                    'message': 'Expected value for sector_product_type to be '
                    'a string or a list of strings but got 3.',
                    'field': 'sector_product_type',
                    'type': 'ValueError',
                },
            ],
        )

    def test_validate_max_product_types(self):
        product_type_count = 60
        product_type_list = [
            'p{}'.format(i) for i in range(1, product_type_count + 1)
        ]
        row = {
            "sector": ['Apparel'],
            "product_type": product_type_list,
        }

        result = self.serializer.validate(row, self.current.copy())
        self.assertEqual(
            result['errors'],
            [
                {
                    'message': 'You may submit a maximum of 50 product types, '
                    'not 60.',
                    'field': 'product_type',
                    'type': 'ValidationError',
                }
            ],
        )

    def test_validate_sector_value_lengths(self):
        row = {
            'sector': [
                ('Agriculture AgricultureAgricultureAgricultureAgricultureAg'
                 'ricultureAgricultureAgricultureAgricultureAgricultureAgric'
                 'ultureAgricultureAgricultureAgricultureAgricultureAgricult'
                 'ureAgricultureAgricultureAgricultureAgricultureAgriculture'
                 )
            ]
        }

        result = self.serializer.validate(row, self.current.copy())
        self.assertEqual(
            result['errors'],
            [
                {
                    'message': ('There is a problem with the sector values: '
                                'Ensure that each value has at most 50 '
                                'characters.'),
                    'field': 'sector',
                    'type': 'ValidationError',
                }
            ],
        )
