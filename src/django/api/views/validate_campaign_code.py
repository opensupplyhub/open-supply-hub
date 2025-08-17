from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from rest_framework import status
from api.helpers.helpers import (
    validate_contributor_campaign_code,
    extract_contributor_id_from_campaign_code
)


@api_view(['GET'])
@throttle_classes([])
def validate_campaign_code(request, code):
    """
    Validates a campaign code and returns contributor information if valid.

    ## Sample Response

        {
            "code": "CC00011",
            "valid": true,
            "contributor_id": 1
        }

    ## Error Response

        {
            "code": "CC00016",
            "valid": false,
            "contributor_id": null
        }

    """
    if not code:
        return Response(
            {
                "code": None,
                "valid": False,
                "contributor_id": None,
                "error": "Campaign code is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    is_valid = validate_contributor_campaign_code(code)
    contributor_id = extract_contributor_id_from_campaign_code(code) if is_valid else None

    return Response({
        "code": code,
        "valid": is_valid,
        "contributor_id": contributor_id
    })