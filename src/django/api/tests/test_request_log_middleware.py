from api.models import Contributor, RequestLog, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from django.urls import reverse


class RequestLogMiddlewareTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        Contributor.objects.create(name=self.name, admin=self.user)

    def test_request_without_token_is_not_logged(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse("facility-list-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, RequestLog.objects.filter(user=self.user).count())

    def test_request_with_token_is_logged(self):
        token = Token.objects.create(user=self.user)
        path = reverse("facility-list-list")
        response = self.client.get(
            path, HTTP_AUTHORIZATION="Token {0}".format(token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, RequestLog.objects.filter(user=self.user).count())

        log = RequestLog.objects.first()
        self.assertEqual(self.user, log.user)
        self.assertEqual(str(token), log.token)
        self.assertEqual("GET", log.method)
        self.assertEqual(path, log.path)
        self.assertEqual(200, log.response_code)
