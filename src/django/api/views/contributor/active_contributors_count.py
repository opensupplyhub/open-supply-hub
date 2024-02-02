from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from .active_contributors import active_contributors


@api_view(['GET'])
@throttle_classes([])
def active_contributors_count(_):
    """
    Returns count of active contributors

    ## Sample Response

        { "count": 14 }
    """
    return Response({
        "count": active_contributors().count()
    })
