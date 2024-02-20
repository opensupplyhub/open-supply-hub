from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from countries.countries import COUNTRY_CHOICES


@api_view(['GET'])
@throttle_classes([])
def all_countries(_):
    """
    Returns a list of country choices as tuples of country codes and names.

    ## Sample Response

        [
            ["AF", "Afghanistan"],
            ["AX", "Åland Islands"]
            ["AL", "Albania"]
        ]

    """
    return Response(COUNTRY_CHOICES)
