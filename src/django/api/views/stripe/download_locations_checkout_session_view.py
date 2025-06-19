import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import permission_classes
from django.shortcuts import redirect
from api.permissions import IsRegisteredAndConfirmed

stripe.api_key = settings.STRIPE_SECRET_KEY
# SITE_URL = settings.SITE_URL if settings.SITE_URL else 'http://localhost:6543'
SITE_URL = 'http://localhost:6543' # Need to define the SITE_URL variable for the different environments


@permission_classes([IsRegisteredAndConfirmed])
class DownloadLocationsCheckoutSessionView(APIView):
    """
    View to create a Stripe Checkout session.
    """
    swagger_schema = None

    def post(self, request, *args, **kwargs):
        """
        Create a Stripe Checkout session.
        """
        # print("request.data >>>", request.data)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1RaadLR1cBat6fnjJqy1dlJM',
                        'quantity': 1,
                        'adjustable_quantity': {
                            'enabled': True,
                            'minimum': 1,
                        },
                    },
                ],
                payment_method_types=['card'],
                mode='payment',
                metadata={
                    'user_email': request.user.email,
                    'user_id': request.user.id,
                },
                allow_promotion_codes=True,
                success_url=SITE_URL + '?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url=SITE_URL + '?canceled=true',
            )

            # return redirect(checkout_session.url)
            return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)
            # return Response(checkout_session, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
