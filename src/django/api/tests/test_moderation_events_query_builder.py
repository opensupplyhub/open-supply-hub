import unittest
from django.test import TestCase
from api.views.v1.opensearch_query_builder. \
    moderation_events_query_builder import ModerationEventsQueryBuilder


class TestModerationEventsQueryBuilder(TestCase):

    def setUp(self):
        self.builder = ModerationEventsQueryBuilder()

    def test_reset(self):
        self.builder.query_body['sort'] = [{"created_at": {"order": "desc"}}]
        self.builder.reset()
        self.assertEqual(self.builder.query_body['sort'], [])

    def test_add_size(self):
        self.builder.add_size(10)
        self.assertEqual(self.builder.query_body['size'], 10)

    def test_add_terms_for_standard_field(self):
        self.builder._add_terms('country', ['US', 'CA'])
        expected = {'terms': {'cleaned_data.country.alpha_2': ['US', 'CA']}}
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
        )

    def test_add_terms_for_os_id(self):
        self.builder._add_terms(
            'os_id',
            ['CN2021250D1DTN7', 'BD2020021QK28YZ']
        )
        expected = {
            'bool': {
                'should': [
                    {
                        'terms': {
                            'os_id': [
                                'CN2021250D1DTN7',
                                'BD2020021QK28YZ'
                            ]
                        }
                    },
                    {
                        'terms': {
                            'historical_os_id.keyword': [
                                'CN2021250D1DTN7',
                                'BD2020021QK28YZ'
                            ]
                        }
                    },
                ]
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
        )

    def test_add_terms_empty_values(self):
        self.builder.add_terms('country', [])
        self.assertEqual(
            self.builder.query_body['query']['bool']['must'],
            []
        )

    def test_add_date_range(self):
        self.builder.__build_date_range({
            'date_gte': '2023-01-01',
            'date_lt': '2023-12-31'
        })
        expected = {
            'range': {
                'created_at': {
                    'gte': '2023-01-01',
                    'lte': '2023-12-31'
                }
            }
        }
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
        )

    def test_add_sort(self):
        self.builder._add_sort('created_at', 'asc')
        expected = {'created_at': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_search_after(self):
        self.builder._add_search_after('test')
        self.assertIn('test', self.builder.query_body['search_after'])
        self.assertIn(
            {'created_at': {'order': 'desc'}},
            self.builder.query_body['sort']
        )

    def test_get_final_query_body(self):
        final_query = self.builder.get_final_query_body()
        expected = {
            'track_total_hits': True,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.assertEqual(final_query, expected)


if __name__ == '__main__':
    unittest.main()
