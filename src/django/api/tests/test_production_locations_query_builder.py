from django.test import TestCase
from unittest.mock import patch
from api.views.v1.opensearch_query_builder. \
    production_locations_query_builder import ProductionLocationsQueryBuilder


class TestProductionLocationsQueryBuilder(TestCase):

    def setUp(self):
        self.builder = ProductionLocationsQueryBuilder()

    def test_reset(self):
        self.builder.query_body['sort'] = [{"name.keyword": {"order": "asc"}}]
        self.builder.reset()
        self.assertEqual(self.builder.query_body['sort'], [])

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

    def test_add_terms_for_standard_field(self):
        self.builder.add_terms('country', ['US', 'CA'])
        expected = {'terms': {'country.alpha_2': ['US', 'CA']}}
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
                                'BD2020021QK28YZ',
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

    def test_add_terms_with_different_field(self):
        self.builder.add_terms('country', ['US', 'CA'])
        self.builder.add_terms('sector', ['Agriculture', 'Apparel'])
        expected_country_terms = {'terms': {'country.alpha_2': ['US', 'CA']}}
        expected_sector_terms = {
            'terms': {'sector.keyword': ['Agriculture', 'Apparel']}
        }
        self.assertIn(
            expected_country_terms,
            self.builder.query_body['query']['bool']['must']
        )
        self.assertIn(
            expected_sector_terms,
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
                'location': {'lat': 40.7128, 'lon': -74.0060}
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

    def test_add_sort_with_default_order(self):
        self.builder.add_sort('name')
        expected = {'name.keyword': {'order': 'asc'}}
        self.assertIn(expected, self.builder.query_body['sort'])

    def test_add_search_after(self):
        search_after_value = 'test_value'
        search_after_id = 'test_id'
        id_type = 'name.keyword'

        self.builder.add_search_after(
            search_after_value,
            search_after_id, id_type
        )

        self.assertEqual(
            self.builder.query_body['search_after'],
            [search_after_value, search_after_id]
        )

        self.assertIn(
            {self.builder.default_sort: self.builder.default_sort_order},
            self.builder.query_body['sort']
        )
        self.assertIn(
            {id_type: self.builder.default_sort_order},
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

    def test_add_multi_match(self):
        self.builder._ProductionLocationsQueryBuilder__add_multi_match(
            'test query'
        )
        expected = {
            'multi_match': {
                'query': 'test query',
                'fields': ['name^2', 'address', 'description', 'local_name'],
                'fuzziness': 2,
            }
        }
        self.assertIn(
            expected, self.builder.query_body['query']['bool']['must']
        )

    def test_add_aggregations_with_precision(self):
        aggregation = 'hexgrid'
        geohex_grid_precision = 5
        self.builder._ProductionLocationsQueryBuilder__add_aggregations(
            aggregation,
            geohex_grid_precision
        )
        expected = {
            'grouped': {
                'geohex_grid': {
                    'field': 'coordinates',
                    'geohex_grid_precision': geohex_grid_precision
                }
            }
        }
        self.assertIn('aggregations', self.builder.query_body)
        self.assertEqual(expected, self.builder.query_body['aggregations'])

    def test_add_aggregations_without_precision(self):
        aggregation = 'hexgrid'
        self.builder._ProductionLocationsQueryBuilder__add_aggregations(
            aggregation
        )
        expected = {
            'grouped': {
                'geohex_grid': {'field': 'coordinates'}
            }
        }
        self.assertIn('aggregations', self.builder.query_body)
        self.assertEqual(expected, self.builder.query_body['aggregations'])

    @patch.object(
        ProductionLocationsQueryBuilder,
        '_ProductionLocationsQueryBuilder__add_aggregations'
    )
    def test_add_specific_queries_with_aggregation(
        self, mock_add_aggregations
    ):
        query_params = {
            'aggregation': 'hexgrid',
        }
        self.builder.add_specific_queries(query_params)

        mock_add_aggregations.assert_called_once_with('hexgrid', None)

    @patch.object(
        ProductionLocationsQueryBuilder,
        '_ProductionLocationsQueryBuilder__add_aggregations'
    )
    def test_add_specific_queries_wit_aggregation_and_precision(
        self, mock_add_aggregations
    ):
        query_params = {
            'aggregation': 'hexgrid',
            'geohex_grid_precision': 4,
        }
        self.builder.add_specific_queries(query_params)

        mock_add_aggregations.assert_called_once_with('hexgrid', 4)

    @patch.object(
        ProductionLocationsQueryBuilder,
        '_ProductionLocationsQueryBuilder__add_multi_match'
    )
    def test_add_specific_queries_with_query(self, mock_add_multi_match):
        query_params = {
            'query': 'search term',
        }
        self.builder.add_specific_queries(query_params)

        mock_add_multi_match.assert_called_once_with('search term')
