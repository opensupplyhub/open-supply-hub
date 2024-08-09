import unittest
from django.test import TestCase
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder


class TestOpenSearchQueryBuilder(TestCase):

    def setUp(self):
        self.builder = OpenSearchQueryBuilder()

    def test_reset(self):
        self.builder.query_body['size'] = 20
        self.builder.reset()
        self.assertEqual(self.builder.query_body['size'], 10)

    def test_add_size(self):
        self.builder.add_size(20)
        self.assertEqual(self.builder.query_body['size'], 20)

    def test_add_match(self):
        self.builder.add_match('name', 'test', fuzziness=1)
        expected = {'match': {'name': {'query': 'test', 'fuzziness': 1}}}
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_multi_match(self):
        self.builder.add_multi_match('test query')
        expected = {
            'multi_match': {
                'query': 'test query',
                'fields': ['name^2', 'address', 'description', 'name_local'],
                'fuzziness': 2
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_terms(self):
        self.builder.add_terms('country', ['US', 'CA'])
        expected = {'terms': {'country.alpha_2': ['US', 'CA']}}
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_range_for_number_of_workers(self):
        self.builder.add_range(
            'number_of_workers',
            {
                'number_of_workers[min]': '10',
                'number_of_workers[max]': '50'
            })
        expected = {
            'bool': {
                'should': [
                    {
                        'bool': {
                            'must': [
                                {
                                    'range': {
                                        'number_of_workers.min': {
                                            'lte': 50,
                                            'gte': 10
                                        }
                                    }
                                },
                                {
                                    'range': {
                                        'number_of_workers.max': {
                                            'gte': 10,
                                            'lte': 50
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_range_for_percent_female_workers(self):
        self.builder.add_range(
            'percent_female_workers',
            {
                'percent_female_workers[min]': '30',
                'percent_female_workers[max]': '60'
            })
        expected = {
            'range': {
                'percent_female_workers': {
                    'gte': 30,
                    'lte': 60
                }
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_geo_distance(self):
        self.builder.add_geo_distance('location', 40.7128, -74.0060, '10km')
        expected = {
            'geo_distance': {
                'distance': '10km',
                'location': {'lat': 40.7128, 'lng': -74.0060}
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
            )

    def test_add_sort(self):
        self.builder.add_sort('name', 'desc')
        expected = {'name.keyword': {'order': 'desc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_search_after(self):
        self.builder.add_search_after('test')
        self.assertIn('test', self.builder.query_body['search_after'])
        self.assertIn(
            {'name.keyword': {'order': 'asc'}},
            self.builder.query_body['sort']
            )

    def test_get_final_query_body(self):
        final_query = self.builder.get_final_query_body()
        expected = {
            'track_total_hits': 'true',
            'size': 10,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.assertEqual(final_query, expected)


if __name__ == '__main__':
    unittest.main()
