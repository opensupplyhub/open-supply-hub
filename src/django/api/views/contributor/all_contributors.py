from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from .active_contributors import active_contributors


@api_view(['GET'])
@throttle_classes([])
def all_contributors(_):
    """
    Returns list contributors as a list of tuples of
    contributor IDs, names and types.

    ## Sample Response

        [
            [1, "Contributor One", "Brand/Retailer"]
            [2, "Contributor Two", "Service Provider"]
        ]
    """
    response_data = [
        (
            contributor.id,
            contributor.name,
            contributor.other_contrib_type
            if contributor.contrib_type == "Other"
            else contributor.contrib_type
        )
        for contributor in active_contributors().order_by('name')
    ]

    return Response(response_data)
