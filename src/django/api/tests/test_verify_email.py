from django.core import signing
from django.urls import reverse
from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.user import User


VERIFY_EMAIL_URL = '/rest-auth/registration/verify-email/'


def make_hmac_key(email_address_pk):
    """Return an HMAC key for the given EmailAddress pk, matching allauth's
    EmailConfirmationHMAC.key property."""
    return signing.dumps(obj=email_address_pk, salt=allauth_settings.SALT)


class VerifyEmailViewTest(APITestCase):

    def setUp(self):
        self.email = 'testuser@example.com'
        self.password = 'S3cur3P@ssword!'
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

    def _create_email_address(self, verified):
        return EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            verified=verified,
            primary=True,
        )

    def test_already_verified_returns_400_with_already_confirmed_code(self):
        email_address = self._create_email_address(verified=True)
        key = make_hmac_key(email_address.pk)

        response = self.client.post(VERIFY_EMAIL_URL, {'key': key})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'already_confirmed')

    def test_unverified_email_is_confirmed_successfully(self):
        email_address = self._create_email_address(verified=False)
        key = make_hmac_key(email_address.pk)

        response = self.client.post(VERIFY_EMAIL_URL, {'key': key})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        email_address.refresh_from_db()
        self.assertTrue(email_address.verified)

    def test_invalid_key_returns_404(self):
        response = self.client.post(VERIFY_EMAIL_URL, {'key': 'invalid-key'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
