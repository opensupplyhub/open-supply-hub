import stripe

from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from api.models import (
    DownloadLocationPayment,
    FacilityDownloadLimit,
    User
)


class DownloadLocationsCheckoutWebhookViewTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.download_limit = FacilityDownloadLimit.objects.create(
            user=self.user,
            free_download_records=100,
            paid_download_records=0,
            updated_at=timezone.now(),
        )

        self.url = reverse('download-locations-checkout-webhook')

    @patch("stripe.Webhook.construct_event")
    def test_invalid_payload_returns_400(self, mock_construct):
        mock_construct.side_effect = ValueError("invalid payload")
        response = self.client.post(
            self.url, data={}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid payload", response.content.decode())

    @patch("stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct):
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "invalid signature", "signature_header"
        )
        response = self.client.post(
            self.url, data={}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid signature", response.content.decode())

    @patch("stripe.checkout.Session.retrieve")
    @patch("stripe.Webhook.construct_event")
    def test_successful_payment_creates_payment_record(self, mock_construct, mock_retrieve):
        session = {
            "metadata": {"user_id": self.user.id},
            "id": "session_123",
            "payment_intent": "pi_789",
            "amount_subtotal": 5000,
            "amount_total": 2500,
            "discounts": [
                {"coupon": "COUPON123", "promotion_code": "PROMO50"},
            ],
        }
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": session},
        }

        mock_line_item = MagicMock()
        mock_line_item.quantity = 2
        mock_line_items = MagicMock()
        mock_line_items.data = [mock_line_item]
        mock_session = MagicMock()
        mock_session.line_items = mock_line_items
        mock_retrieve.return_value = mock_session

        response = self.client.post(
            self.url, data={}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        payment = DownloadLocationPayment.objects.get(user_id=self.user.id)

        self.assertEqual(payment.stripe_session_id, "session_123")
        self.assertEqual(payment.payment_id, "pi_789")
        self.assertEqual(payment.amount_subtotal, 5000)
        self.assertEqual(payment.amount_total, 2500)
        self.assertEqual(
            payment.discounts,
            [
                {"coupon": "COUPON123", "promotion_code": "PROMO50"},
            ],
        )

    @patch("stripe.Webhook.construct_event")
    def test_missing_field_returns_400(self, mock_construct):
        session = {
            "metadata": {"user_id": self.user.id},
            "id": "session_123",
            # Missing payment_intent
            "amount_subtotal": 5000,
            "amount_total": 2500,
        }
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": session},
        }

        response = self.client.post(
            self.url, data={}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing expected field", response.content.decode())

    @patch(
        "api.views.stripe.download_locations_checkout_webhook_view"
        ".DownloadLocationPayment.save"
    )
    @patch("stripe.Webhook.construct_event")
    def test_unexpected_error_returns_500(self, mock_construct, mock_save):
        session = {
            "metadata": {"user_id": self.user.id},
            "id": "session_123",
            "payment_intent": "pi_789",
            "amount_subtotal": 5000,
            "amount_total": 2500,
            "discounts": [
                {"coupon": "COUPON123", "promotion_code": "PROMO50"},
            ],
        }
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": session},
        }

        mock_save.side_effect = Exception("db error")

        response = self.client.post(
            self.url, data={}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Unexpected error", response.content.decode())
