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
        self.builder.add_terms('country', ['US', 'CA'])
        expected = {'terms': {'cleaned_data.country.alpha_2': ['US', 'CA']}}
        self.assertIn(
            expected,
            self.builder.query_body['query']['bool']['must']
        )

    def test_add_terms_for_os_id(self):
        self.builder.add_terms(
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
        self.builder._OpenSearchQueryBuilder__build_date_range({
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
        self.builder.add_sort('created_at', 'asc')
        expected = {'created_at': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_sort_with_default_order(self):
        self.builder.add_sort('created_at')
        expected = {'created_at': {'order': 'desc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_sort_name(self):
        self.builder.add_sort('name', 'asc')
        expected = {'cleaned_data.name': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_sort_address(self):
        self.builder.add_sort('address', 'asc')
        expected = {'cleaned_data.address': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_sort_country(self):
        self.builder.add_sort('country', 'asc')
        expected = {'cleaned_data.country.name': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_search_after(self):
        search_after_value = '2023-11-21T10:00:00'
        search_after_id = '123e4567-e89b-12d3-a456-426614174000'
        id_type = 'moderation_id'

        self.builder.add_search_after(
            search_after_value,
            search_after_id, id_type
        )

        self.assertEqual(
            [{'created_at': 'desc'}, {'moderation_id': 'desc'}],
            self.builder.query_body['sort']
        )

        self.assertEqual(
            self.builder.query_body['search_after'],
            [search_after_value, search_after_id]
        )

    def test_get_final_query_body(self):
        final_query = self.builder.get_final_query_body()
        expected = {
            'track_total_hits': True,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.assertEqual(final_query, expected)
