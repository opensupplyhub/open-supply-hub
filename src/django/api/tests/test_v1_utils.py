from django.test import TestCase
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_value_error,
    handle_opensearch_exception
)
from api.services.search import OpenSearchServiceException


class TestProductionLocationsSerializer(serializers.Serializer):
    size = serializers.IntegerField(required=False)
    address = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    search_after = serializers.CharField(required=False)
    number_of_workers_min = serializers.IntegerField(required=False)
    number_of_workers_max = serializers.IntegerField(required=False)
    percent_female_workers_min = serializers.FloatField(required=False)
    percent_female_workers_max = serializers.FloatField(required=False)
    coordinates_lat = serializers.FloatField(required=False)
    coordinates_lon = serializers.FloatField(required=False)
    country = serializers.ListField(
        child=serializers.CharField(required=False),
        required=False
    )
    sort_by = serializers.ChoiceField(
        choices=['name', 'address'],
        required=False
    )
    order_by = serializers.ChoiceField(
        choices=['asc', 'desc'],
        required=False
    )


class V1UtilsTests(TestCase):

    def test_serialize_params_with_deep_object(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': '10',
            'number_of_workers[max]': '50',
            'percent_female_workers[min]': '20',
            'percent_female_workers[max]': '80',
            'coordinates[lat]': '12.34',
            'coordinates[lon]': '56.78',
        })
        serialized_params, error_response = \
            serialize_params(TestProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['number_of_workers_min'], 10)
        self.assertEqual(serialized_params['number_of_workers_max'], 50)
        self.assertEqual(serialized_params['percent_female_workers_min'], 20)
        self.assertEqual(serialized_params['percent_female_workers_max'], 80)
        self.assertEqual(serialized_params['coordinates_lat'], 12.34)
        self.assertEqual(serialized_params['coordinates_lon'], 56.78)

    def test_serialize_params_with_single_values(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'address': '123 Main St',
            'description': 'A great place',
            'search_after': 'abc123',
            'sort_by': 'name',
            'order_by': 'asc',
            'size': 10
        })
        serialized_params, error_response = \
            serialize_params(TestProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['address'], '123 Main St')
        self.assertEqual(serialized_params['description'], 'A great place')
        self.assertEqual(serialized_params['search_after'], 'abc123')
        self.assertEqual(serialized_params['sort_by'], 'name')
        self.assertEqual(serialized_params['order_by'], 'asc')
        self.assertEqual(serialized_params['size'], 10)

    def test_serialize_params_with_mixed_values(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': '10',
            'address': '123 Main St',
        })
        serialized_params, error_response = \
            serialize_params(TestProductionLocationsSerializer, query_dict)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['number_of_workers_min'], 10)
        self.assertEqual(serialized_params['address'], '123 Main St')

    def test_serialize_params_invalid(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update({
            'number_of_workers[min]': 'not_a_number',
            'size': 'not_a_number'
        })
        serialized_params, error_response = \
            serialize_params(TestProductionLocationsSerializer, query_dict)
        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response['message'],
            "The request query is invalid."
        )
        self.assertIn(
            {
                'field': 'number_of_workers_min',
                'message': 'A Valid Integer Is Required.'
            },
            error_response['errors']
        )
        self.assertIn(
            {
                'field': 'size',
                'message': 'A Valid Integer Is Required.'
            },
            error_response['errors']
        )

    def test_handle_value_error(self):
        exception = ValueError("Test error")
        response = handle_value_error(exception)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            "The request query is invalid."
        )
        self.assertEqual(response.data['errors'][0]['field'], "general")
        self.assertIn(
            "There was a problem processing your request.",
            response.data['errors'][0]['message']
        )

    def test_handle_opensearch_exception(self):
        exception = OpenSearchServiceException("OpenSearch error")
        response = handle_opensearch_exception(exception)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['message'], "OpenSearch error")
