from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from api.constants import FacilityClaimStatuses


@api_view(['GET'])
@throttle_classes([])
def claim_statuses(_):
    """
    Returns a list of claim statuses.

    ## Sample Response

        [
            "PENDING"
            "APPROVED"
            "DENIED"
            "REVOKED"
        ]

    """
    statuses = [
        FacilityClaimStatuses.PENDING,
        FacilityClaimStatuses.APPROVED,
        FacilityClaimStatuses.DENIED,
        FacilityClaimStatuses.REVOKED
    ]
    return Response(statuses)
