from django.test import TestCase
from rest_framework import serializers
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_value_error,
    handle_opensearch_exception
)
from api.services.search import OpenSearchServiceException


class TestSerializer(serializers.Serializer):
    field = serializers.CharField()


class V1UtilsTests(TestCase):

    def test_serialize_params_valid(self):
        params = {'field': 'value'}
        serializer_class = TestSerializer
        serialized_params, error_response = \
            serialize_params(serializer_class, params)
        self.assertIsNone(error_response)
        self.assertEqual(serialized_params['field'], 'value')

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
