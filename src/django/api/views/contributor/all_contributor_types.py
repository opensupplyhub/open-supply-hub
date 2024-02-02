from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from ...models import Contributor


@api_view(['GET'])
@throttle_classes([])
def all_contributor_types(_):
    """
    Returns a list of contributor type choices as tuples of values and display
    names.

    ## Sample Response

        [
            ["Auditor", "Auditor"],
            ["Brand/Retailer", "Brand/Retailer"],
            ["Civil Society Organization", "Civil Society Organization"],
            ["Factory / Facility", "Factory / Facility"]
        ]
    """
    return Response(Contributor.CONTRIB_TYPE_CHOICES)
