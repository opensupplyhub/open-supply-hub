from django.test import TestCase
from django.http import QueryDict
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_value_error,
    handle_opensearch_exception
)
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
from api.services.opensearch.search import OpenSearchServiceException


class V1UtilsTests(TestCase):

    def test_serialize_params_with_deep_object(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': '10',
            'number_of_workers[max]': '50',
            'percent_female_workers[min]': '20',
            'percent_female_workers[max]': '80',
            'coordinates[lat]': '12.34',
            'coordinates[lng]': '56.78',
        })
        serialized_params, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['number_of_workers_min'], 10)
        self.assertEqual(serialized_params['number_of_workers_max'], 50)
        self.assertEqual(serialized_params['percent_female_workers_min'], 20)
        self.assertEqual(serialized_params['percent_female_workers_max'], 80)
        self.assertEqual(serialized_params['coordinates_lat'], 12.34)
        self.assertEqual(serialized_params['coordinates_lng'], 56.78)

    def test_serialize_params_with_single_values(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'address': '123 Main St',
            'description': 'Production location description',
            'search_after[id]': 'TR2209172HY45SD',
            'search_after[value]': 'abc123',
            'sort_by': 'name',
            'order_by': 'asc',
            'size': 10,
            'aggregation': 'geohex_grid',
            'geohex_grid_precision': 2,
        })
        serialized_params, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['address'], '123 Main St')
        self.assertEqual(
            serialized_params['description'],
            'Production location description'
        )
        self.assertEqual(serialized_params['search_after_value'], 'abc123')
        self.assertEqual(
            serialized_params['search_after_id'],
            'TR2209172HY45SD'
        )
        self.assertEqual(serialized_params['sort_by'], 'name')
        self.assertEqual(serialized_params['order_by'], 'asc')
        self.assertEqual(serialized_params['size'], 10)
        self.assertEqual(serialized_params['aggregation'], 'geohex_grid')
        self.assertEqual(serialized_params['geohex_grid_precision'], 2)

    def test_serialize_params_with_mixed_values(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': '10',
            'number_of_workers[max]': '50',
            'address': '123 Main St',
        })
        serialized_params, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['number_of_workers_min'], 10)
        self.assertEqual(serialized_params['number_of_workers_max'], 50)
        self.assertEqual(serialized_params['address'], '123 Main St')

    def test_serialize_params_invalid(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': 'not_a_number',
            'size': 'not_a_number'
        })
        _, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'],
            "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'number_of_workers_min',
                'detail': 'A valid integer is required.'
            },
            error_response['errors']
        )
        self.assertIn(
            {
                'field': 'size',
                'detail': 'A valid integer is required.'
            },
            error_response['errors']
        )

    def test_serialize_invalid_aggregation(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'aggregation': 'invalid_aggregation',
        })
        _, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertIn(
            {
                'field': 'aggregation',
                'detail': '"invalid_aggregation" is not a valid choice.'
            },
            error_response['errors']
        )

    def test_serialize_invalid_precision_type(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'geohex_grid_precision': 'not_a_number',
        })
        _, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertIn(
            {
                'field': 'geohex_grid_precision',
                'detail': 'A valid integer is required.'
            },
            error_response['errors']
        )

    def test_serialize_precision_value_too_low(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'geohex_grid_precision': '-1',
        })
        _, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertIn(
            {
                'field': 'geohex_grid_precision',
                'detail': 'Ensure this value is greater than or equal to 0.'
            },
            error_response['errors']
        )

    def test_serialize_precision_value_too_high(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'geohex_grid_precision': '16',
        })
        _, error_response = \
            serialize_params(ProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertIn(
            {
                'field': 'geohex_grid_precision',
                'detail': 'Ensure this value is less than or equal to 15.'
            },
            error_response['errors']
        )

    def test_handle_value_error(self):
        exception = ValueError("Test error")
        response = handle_value_error(exception)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            "The request query is invalid."
        )
        self.assertEqual(response.data['errors'][0]['field'],
                         "non_field_errors")
        self.assertIn(
            "There was a problem processing your request.",
            response.data['errors'][0]['detail']
        )

    def test_handle_opensearch_exception(self):
        exception = OpenSearchServiceException("OpenSearch error")
        response = handle_opensearch_exception(exception)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['detail'], "OpenSearch error")

    def test_serialize_geo_bounding_box(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(
            {
                'geo_bounding_box[top]': '90',
                'geo_bounding_box[left]': '-180',
                'geo_bounding_box[bottom]': '-90',
                'geo_bounding_box[right]': '180',
            }
        )
        serialized_params, error_response = serialize_params(
            ProductionLocationsSerializer, query_dict
        )
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['geo_bounding_box_top'], 90)
        self.assertEqual(serialized_params['geo_bounding_box_left'], -180)
        self.assertEqual(serialized_params['geo_bounding_box_bottom'], -90)
        self.assertEqual(serialized_params['geo_bounding_box_right'], 180)

    def test_serialize_geo_bounding_box_missing_values(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(
            {
                'geo_bounding_box[top]': '90',
                'geo_bounding_box[left]': '-180',
                'geo_bounding_box[bottom]': '-90',
            }
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer, query_dict
        )
        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'], "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'geo_bounding_box',
                'detail': 'All coordinates (top, left, bottom, right) '
                'must be provided.',
            },
            error_response['errors'],
        )

    def test_serialize_geo_bounding_box_invalid_range(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(
            {
                'geo_bounding_box[top]': '91',
                'geo_bounding_box[left]': '-180',
                'geo_bounding_box[bottom]': '-90',
                'geo_bounding_box[right]': '181',
            }
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer, query_dict
        )

        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'], "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'geo_bounding_box',
                'detail': 'The top value must be between -90 and 90.',
            },
            error_response['errors'],
        )
        self.assertIn(
            {
                'field': 'geo_bounding_box',
                'detail': 'The right value must be between -180 and 180.',
            },
            error_response['errors'],
        )

    def test_serialize_geo_bounding_box_invalid_order(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(
            {
                'geo_bounding_box[top]': '-90',
                'geo_bounding_box[left]': '180',
                'geo_bounding_box[bottom]': '90',
                'geo_bounding_box[right]': '-180',
            }
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer, query_dict
        )

        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'], "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'geo_bounding_box',
                'detail': 'The right must be greater than left.',
            },
            error_response['errors'],
        )
        self.assertIn(
            {
                'field': 'geo_bounding_box',
                'detail': 'The top must be greater than bottom.',
            },
            error_response['errors'],
        )

    def test_serialize_geo_polygon_invalid_format(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.setlist('geo_polygon', ['invalid_coordinate'])
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            query_dict
        )

        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'],
            "The request query is invalid."
        )

        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'Invalid coordinate format: invalid_coordinate, '
                    "must be 'lat,lon' as floats."
                ),
            },
            error_response['errors'],
        )

    def test_serialize_geo_polygon_out_of_bounds(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.setlist(
            'geo_polygon',
            ['91,45', '-91,100', '30,181', '45,-181']
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            query_dict
        )

        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'],
            "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'Invalid latitude 91.0, '
                    'must be between -90 and 90.'
                )
            },
            error_response['errors'],
        )
        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'Invalid latitude -91.0, '
                    'must be between -90 and 90.'
                )
            },
            error_response['errors'],
        )
        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'Invalid longitude 181.0, '
                    'must be between -180 and 180.'
                )
            },
            error_response['errors'],
        )
        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'Invalid longitude -181.0, '
                    'must be between -180 and 180.'
                )
            },
            error_response['errors'],
        )

    def test_serialize_geo_polygon_not_enough_points(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.setlist(
            'geo_polygon',
            ['91,45', '-91,100']
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            query_dict
        )

        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['detail'],
            "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'geo_polygon',
                'detail': (
                    'At least 3 points are required in '
                    'geo_polygon to form a valid polygon.'
                )
            },
            error_response['errors'],
        )

    def test_serialize_geo_polygon_valid(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.setlist(
            'geo_polygon',
            ['40.7128,-74.0060', '34.0522,-118.2437', '51.5074,-0.1278']
        )
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            query_dict
        )

        self.assertIsNone(error_response)
