from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from .active_contributors import active_contributors


@api_view(['GET'])
@throttle_classes([])
def all_contributors(_):
    """
    Returns list contributors as a list of tuples of contributor IDs and names.

    ## Sample Response

        [
            [1, "Contributor One"]
            [2, "Contributor Two"]
        ]
    """
    response_data = [
        (contributor.id, contributor.name)
        for contributor
        in active_contributors().order_by('name')
    ]

    return Response(response_data)
