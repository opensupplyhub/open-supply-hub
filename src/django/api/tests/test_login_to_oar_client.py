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

    def test_missing_email_or_password(self):
        response = self.client.post(
            self.login_url, {'email': 'testuser@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'Email and password are required', response.data['detail']
        )

    def test_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'email': 'testuser@example.com', 'password': 'wrongpassword'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'Unable to login with those credentials', response.data['detail']
        )

    def test_unconfirmed_user_login(
        self,
    ):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )
        response = self.client.post(
            self.login_url,
            {
                'email': 'testuser@example.com',
                'password': 'password',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'Your account is not verified. '
            'Check your email for a confirmation link.',
            response.data['detail'],
        )

    def test_successful_login(self):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=True, primary=True
        )

        response = self.client.post(
            self.login_url,
            {'email': 'testuser@example.com', 'password': 'password'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def test_successful_login_with_uppercase_email(self):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=True, primary=True
        )
        response = self.client.post(
            self.login_url,
            {'email': 'TESTUSER@EXAMPLE.COM', 'password': 'password'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def test_successful_login_with_mixed_case_email(self):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=True, primary=True
        )
        response = self.client.post(
            self.login_url,
            {'email': 'TestUser@Example.Com', 'password': 'password'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def unconfirmed_user_login_with_uppercase_email(self):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )
        response = self.client.post(
            self.login_url,
            {'email': 'TestUser@example.Com', 'password': 'password'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'Your account is not verified. '
            'Check your email for a confirmation link.',
            response.data['detail'],
        )

    def test_unconfirmed_user_login_resends_confirmation_email(self):
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.email, verified=False, primary=True
        )

        with patch.object(
            EmailAddress, 'send_confirmation'
        ) as mock_send_confirmation:
            response = self.client.post(
                self.login_url,
                {
                    'email': 'testuser@example.com',
                    'password': 'password',
                },
            )

            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )
            self.assertIn(
                'Your account is not verified. '
                'Check your email for a confirmation link.',
                response.data['detail'],
            )
            mock_send_confirmation.assert_called_once()
