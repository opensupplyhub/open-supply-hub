import stripe
from django.conf import settings
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest


class DownloadLocationsCheckoutWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponseBadRequest(f"Invalid payload: {str(e)}", status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponseBadRequest(f"Invalid signature: {str(e)}", status=400)
        
        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print("Checkout session completed >>>", session)

        return HttpResponse(status=200)
