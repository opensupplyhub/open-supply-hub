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
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.login_url = reverse('login_to_oar_client')

    def create_email_address(self, verified):
        return EmailAddress.objects.create(
            user=self.user, email=self.email, verified=verified, primary=True
        )

    def test_missing_email_or_password(self):
        response = self.client.post(self.login_url, {'email': self.email})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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
        self.create_email_address(verified=False)
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
        self.create_email_address(verified=True)
        response = self.client.post(
            self.login_url, {'email': self.email, 'password': self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.email)

    def test_successful_login_with_various_case_emails(self):
        self.create_email_address(verified=True)
        test_cases = ['TESTUSER@EXAMPLE.COM', 'TestUser@Example.Com']
        for case in test_cases:
            with self.subTest(email=case):
                response = self.client.post(
                    self.login_url, {'email': case, 'password': self.password}
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['email'], self.email)

    def test_unconfirmed_user_login_with_various_case_emails(self):
        self.create_email_address(verified=False)
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
        self.create_email_address(verified=False)
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

    def test_login_compare_csrf_token(self):
        self.create_email_address(verified=True)
        response = self.client.post(
            self.login_url, {'email': self.email, 'password': self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.email)

        csrf_token_cookie = response.client.cookies.get('csrftoken')
        csrf_token_data = response.data['csrfToken']

        self.assertEqual(csrf_token_cookie.value, csrf_token_data)
