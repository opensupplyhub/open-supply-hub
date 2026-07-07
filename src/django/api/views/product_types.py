from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.cache import cache_page

from ..extended_fields import get_product_types


@api_view(['GET'])
@throttle_classes([])
@cache_page(
    settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS,
    cache="view_cache",
)
def product_types(_):
    """
    Returns a list of suggested product types by combining standard types with
    distinct values submitted by contributors.

    ## Sample Response

        [
            "Accessories",
            "Belts",
            "Caps"
        ]

    """
    return Response(get_product_types())
