from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase


class HealthCheckPingEndpointTest(TestCase):
    def test_ping_returns_pong_without_watchman_payload(self):
        response = self.client.get('/health-check/ping/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'pong')
        self.assertNotIn(b'databases', response.content)
        self.assertNotIn(b'caches', response.content)


class OriginSourceMiddlewareHealthCheckTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpResponse(status=200)

    @patch('api.middleware.connection')
    def test_skips_database_set_for_health_check_ping(self, mock_connection):
        from api.middleware import OriginSourceMiddleware

        middleware = OriginSourceMiddleware(self.get_response)
        request = self.factory.get('/health-check/ping/')

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        mock_connection.cursor.assert_not_called()

    @patch('api.middleware.connection')
    def test_sets_origin_source_for_non_health_paths(self, mock_connection):
        from api.middleware import OriginSourceMiddleware

        cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = cursor

        middleware = OriginSourceMiddleware(self.get_response)
        request = self.factory.get('/api/facilities/')

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        cursor.execute.assert_called_once()


class DarkVisitorsMiddlewareHealthCheckTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpResponse(status=200)

    def test_skips_dark_visitors_for_health_check_paths(self):
        from api.middleware import DarkVisitorsMiddleware

        middleware = DarkVisitorsMiddleware(self.get_response)
        middleware.TOKEN = 'dummy-token'
        middleware.executor = MagicMock()

        request = self.factory.get('/health-check/ping/')
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        middleware.executor.submit.assert_not_called()
