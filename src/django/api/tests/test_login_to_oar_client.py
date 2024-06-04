from unittest.mock import patch
from django.urls import reverse
from api.models.user import User
from rest_framework import status
from allauth.account.models import EmailAddress
from rest_framework.test import APITestCase


class LoginToOARClientTest(APITestCase):

    def setUp(self):
        self.email = 'testuser@example.com'
        self.password = 'password'
        self.user = User.objects.create_user(
            email=self.email, password=self.password
        )
        self.login_url = reverse('login_to_oar_client')

    def test_missing_email_or_password(self):
        response = self.client.post(self.login_url, {'email': self.email})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'], 'Email and password are required'
        )

    def test_invalid_credentials(self):
        response = self.client.post(
            self.login_url, {'email': self.email, 'password': 'wrongpassword'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'], 'Unable to login with those credentials'
        )

    def test_unconfirmed_user_login(self):
        EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )
        response = self.client.post(
            self.login_url, {'email': self.email, 'password': self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            'Your account is not verified. '
            'Check your email for a confirmation link.',
        )

    def test_successful_login(self):
        EmailAddress.objects.create(
            user=self.user, email=self.email, verified=True, primary=True
        )
        response = self.client.post(
            self.login_url, {'email': self.email, 'password': self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.email)

    def test_successful_login_with_various_case_emails(self):
        EmailAddress.objects.create(
            user=self.user, email=self.email, verified=True, primary=True
        )
        test_cases = ['TESTUSER@EXAMPLE.COM', 'TestUser@Example.Com']
        for case in test_cases:
            with self.subTest(email=case):
                response = self.client.post(
                    self.login_url, {'email': case, 'password': self.password}
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['email'], self.email)

    def test_unconfirmed_user_login_with_various_case_emails(self):
        EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )
        test_cases = ['TESTUSER@EXAMPLE.COM', 'TestUser@Example.Com']
        for case in test_cases:
            with self.subTest(email=case):
                response = self.client.post(
                    self.login_url, {'email': case, 'password': self.password}
                )
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )
                self.assertEqual(
                    response.data['detail'],
                    'Your account is not verified. '
                    'Check your email for a confirmation link.',
                )

    def test_unconfirmed_user_login_resends_confirmation_email(self):
        EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )
        with patch.object(
            EmailAddress, 'send_confirmation'
        ) as mock_send_confirmation:
            response = self.client.post(
                self.login_url,
                {'email': self.email, 'password': self.password},
            )
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )
            self.assertEqual(
                response.data['detail'],
                'Your account is not verified. '
                'Check your email for a confirmation link.',
            )
            mock_send_confirmation.assert_called_once()
