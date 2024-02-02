from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from api.constants import NumberOfWorkersRanges


@api_view(['GET'])
@throttle_classes([])
def number_of_workers_ranges(_):
    """
    Returns a list of standardized ranges for the number_of_workers extended
    field.

    ## Sample Response

        [
            "Less than 1000",
            "1001-5000",
            "5001-10000",
            "More than 10000",
        ]

    """
    return Response([
        r['label'] for r in NumberOfWorkersRanges.STANDARD_RANGES
    ])
