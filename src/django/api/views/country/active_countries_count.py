from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from ...models.facility.facility_index import FacilityIndex


@api_view(['GET'])
@throttle_classes([])
def active_countries_count(_):
    """
    Returns a count of disctinct country codes for active facilities.

    ## Sample Response

        { "count": 52 }
    """

    count = (
        FacilityIndex
        .objects
        .values_list('country_code')
        .distinct()
        .count()
    )

    return Response({"count": count})
