import stripe

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsRegisteredAndConfirmed

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_PRICE_ID = settings.STRIPE_PRICE_ID


class DownloadLocationsCheckoutSessionView(APIView):
    """
    View to create a Stripe Checkout session for purchasing additional records
    for downloading production locations data.
    """

    permission_classes = [IsRegisteredAndConfirmed]
    swagger_schema = None

    def post(self, request, *args, **kwargs):
        site_url = request.build_absolute_uri('/')

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': STRIPE_PRICE_ID,
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
                    'user_id': request.user.id,
                },
                allow_promotion_codes=True,
                success_url=site_url + 'facilities?success=true',
                cancel_url=site_url + 'facilities?canceled=true',
            )

            return Response(
                {'url': checkout_session.url}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
