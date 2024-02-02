from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from ...models.facility.facility import Facility


@api_view(['GET'])
@throttle_classes([])
def current_tile_cache_key(_):
    return Response(
        Facility.current_tile_cache_key()
    )
