from rest_framework.exceptions import ValidationError
from rest_framework.decorators import (
    api_view,
    permission_classes,
    renderer_classes,
    throttle_classes,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from waffle.decorators import waffle_switch
from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.views.decorators.cache import cache_control
from django.db import transaction

from ...exceptions import BadRequestException
from ...permissions import IsAllowedHost
from ...renderers import MvtRenderer
from ...serializers import FacilityQueryParamsSerializer
from ...tiler import (
    get_facilities_vector_tile,
    get_facility_grid_vector_tile
)
from api.views.tile.utils import (
    retrieve_cached_tile,
    is_tile_cache_valid
)


@api_view(['GET'])
@permission_classes([IsAllowedHost])
@renderer_classes([MvtRenderer])
@cache_control(max_age=settings.TILE_CACHE_MAX_AGE_IN_SECONDS)
@throttle_classes([])
@waffle_switch('vector_tile')
@transaction.atomic
def get_tile(request, layer, cachekey, z, x, y, ext):
    if cachekey is None:
        raise BadRequestException('missing cache key')

    if layer not in ['facilities', 'facilitygrid']:
        raise BadRequestException(f'invalid layer name: {layer}')

    if ext != 'pbf':
        raise BadRequestException(f'invalid extension: {ext}')

    params = FacilityQueryParamsSerializer(data=request.query_params)

    if not params.is_valid():
        raise ValidationError(params.errors)

    cached_tile, created = retrieve_cached_tile(request.get_full_path())
    if not created and is_tile_cache_valid(cached_tile.created_at):
        cached_tile.counter += 1
        cached_tile.save()

        return Response(cached_tile.value)

    try:
        tile = {
            'facilities': get_facilities_vector_tile(
                request.query_params, layer, z, x, y),
            'facilitygrid': get_facility_grid_vector_tile(
                request.query_params, layer, z, x, y)
        }[layer]
        cached_tile.value = tile.tobytes()
        cached_tile.counter = 0
        cached_tile.embed = bool(params.validated_data['embed'])
        cached_tile.contributors = params.validated_data['contributors']
        cached_tile.save()
        return Response(cached_tile.value)
    except EmptyResultSet:
        return Response(None, status=HTTP_204_NO_CONTENT)
