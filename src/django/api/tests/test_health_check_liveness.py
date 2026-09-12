from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase


class HealthCheckEndpointTest(TestCase):
    def test_health_check_is_app_liveness_only(self):
        response = self.client.get('/health-check/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
        self.assertNotIn(b'databases', response.content)
        self.assertNotIn(b'caches', response.content)


class OriginSourceMiddlewareHealthCheckTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpResponse(status=200)

    @patch('api.middlewares.origin_source.connection')
    def test_skips_database_set_for_health_check(self, mock_connection):
        from api.middlewares.origin_source import OriginSourceMiddleware

        middleware = OriginSourceMiddleware(self.get_response)
        request = self.factory.get('/health-check/')

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        mock_connection.cursor.assert_not_called()

    @patch('api.middlewares.origin_source.connection')
    def test_sets_origin_source_for_non_health_paths(self, mock_connection):
        from api.middlewares.origin_source import OriginSourceMiddleware

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

        request = self.factory.get('/health-check/')
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        middleware.executor.submit.assert_not_called()
