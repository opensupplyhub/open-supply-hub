from types import SimpleNamespace
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from api.models import User
import api.views.stripe.download_locations_checkout_session_view as checkout_session


class DownloadLocationsCheckoutSessionViewTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.client.login(email=self.email, password=self.password)
        self.url = reverse('download-locations-checkout-session')

    @patch('stripe.checkout.Session.create')
    def test_checkout_session_creation(self, mock_create):
        checkout_session.STRIPE_PRICE_ID = "price_test_123"

        fake_url = 'https://checkout.stripe.com/session_id'
        mock_create.return_value = SimpleNamespace(url=fake_url)

        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.data)
        self.assertEqual(response.data['url'], fake_url)

        expected_line_items = [
            {
                'price': 'price_test_123',
                'quantity': 1,
                'adjustable_quantity': {
                    'enabled': True,
                    'minimum': 1,
                },
            },
        ]

        mock_create.assert_called_once_with(
            line_items=expected_line_items,
            payment_method_types=['card'],
            mode='payment',
            metadata={'user_id': self.user.id},
            allow_promotion_codes=True,
            success_url='http://testserver/facilities',
            cancel_url='http://testserver/facilities',
        )

    @patch('stripe.checkout.Session.create')
    def test_checkout_session_creation_error(self, mock_create):
        mock_create.side_effect = Exception("Stripe error")

        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Stripe error")

    def test_checkout_session_requires_authentication(self):
        self.client.logout()
        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.',
        )
