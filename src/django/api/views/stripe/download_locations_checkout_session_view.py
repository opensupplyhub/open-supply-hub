from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsRegisteredAndConfirmed
from api.services.facilities_download_service import FacilitiesDownloadService


class DownloadLocationsCheckoutSessionView(APIView):
    """
    View to create a Stripe Checkout session for purchasing additional records
    for downloading production locations data.
    """

    permission_classes = [IsRegisteredAndConfirmed]
    swagger_schema = None

    def post(self, request, *args, **kwargs):
        site_url = request.build_absolute_uri('/').rstrip('/')

        try:
            FacilitiesDownloadService \
                .get_download_limit(request)

            redirect_path = request.data.get('redirect_path')
            checkout_url = FacilitiesDownloadService \
                .get_checkout_url(
                    request.user.id,
                    site_url + redirect_path
                )

            return Response(
                {'url': checkout_url}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
