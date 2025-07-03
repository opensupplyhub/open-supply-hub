from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
from api.middleware import DarkVisitorsMiddleware


class DarkVisitorsMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpResponse(status=200)

    @patch('api.middleware.requests.post')
    def test_sends_post_request_when_token_present(self, mock_post):
        middleware = DarkVisitorsMiddleware(self.get_response)
        middleware.TOKEN = 'dummy-token'
        fake_executor = MagicMock()
        middleware.executor = fake_executor

        request = self.factory.get(
            '/test-url',
            HTTP_USER_AGENT='TestAgent',
            HTTP_REFERER='https://example.com',
            HTTP_HOST='testserver',
            HTTP_AUTHORIZATION='Bearer should-be-filtered',
            HTTP_X_CUSTOM='nope',
        )

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

        expected_payload = {
            'request_path': '/test-url',
            'request_method': 'GET',
            'request_headers': {
                'User-Agent': 'TestAgent',
                'Referer': 'https://example.com',
                'Host': 'testserver',
            },
        }
        expected_headers = {
            'Authorization': 'Bearer dummy-token',
            'Content-Type': 'application/json',
        }

        fake_executor.submit.assert_called_once_with(
            mock_post,
            DarkVisitorsMiddleware.API_URL,
            json=expected_payload,
            headers=expected_headers,
        )

    @patch('api.middleware.requests.post')
    def test_does_not_send_post_when_no_token(self, mock_post):
        middleware = DarkVisitorsMiddleware(self.get_response)
        middleware.TOKEN = None
        fake_executor = MagicMock()
        middleware.executor = fake_executor

        request = self.factory.get('/test-url')

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        fake_executor.submit.assert_not_called()
        mock_post.assert_not_called()
