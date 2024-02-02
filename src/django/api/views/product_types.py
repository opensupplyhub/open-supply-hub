from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response

from ..extended_fields import get_product_types


@api_view(['GET'])
@throttle_classes([])
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
