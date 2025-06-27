import stripe

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from api.models import DownloadLocationPayment


class DownloadLocationsCheckoutWebhookView(View):
    """
    View to handle Stripe Checkout webhook events for
    successful payments of additional records for downloading production
    locations data.
    """

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponseBadRequest(
                f"Invalid payload: {str(e)}", status=400
            )
        except stripe.error.SignatureVerificationError as e:
            return HttpResponseBadRequest(
                f"Invalid signature: {str(e)}", status=400
            )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            try:
                user_id = session["metadata"]["user_id"]
                stripe_session_id = session["id"]
                payment_id = session["payment_intent"]
                amount_subtotal = session["amount_subtotal"]
                amount_total = session["amount_total"]
                discounts = session["discounts"]

                payment = DownloadLocationPayment(
                    user_id=user_id,
                    stripe_session_id=stripe_session_id,
                    payment_id=payment_id,
                    amount_subtotal=amount_subtotal,
                    amount_total=amount_total,
                    discounts=discounts,
                )
                payment.save()

            except KeyError as e:
                return HttpResponseBadRequest(f"Missing expected field: {e}")
            except Exception as e:
                return HttpResponse(f"Unexpected error: {str(e)}", status=500)

        return HttpResponse(status=200)
