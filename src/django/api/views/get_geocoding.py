from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..geocoding import geocode_address
from ..exceptions import BadRequestException


@api_view(['GET'])
@throttle_classes([])
@permission_classes([IsAdminUser])
def get_geocoding(request):
    """
    Returns geocoded name and address.
    """
    country_code = request.query_params.get('country_code', None)
    address = request.query_params.get('address', None)

    if country_code is None:
        raise BadRequestException('Missing country code')

    if address is None:
        raise BadRequestException('Missing address')

    geocode_result = geocode_address(address, country_code)
    return Response(geocode_result)
