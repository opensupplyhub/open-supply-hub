from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response

from api.models import ClaimAffiliation, ClaimCertification


@api_view(['GET'])
@throttle_classes([])
def claim_profile_options(_):
    """
    Returns the affiliations and certifications/standards/regulations
    the claim form currently offers, in display order. Both lists are
    managed in the Django admin.

    ## Sample Response

        {
            "affiliations": [
                "Better Work (ILO)",
                "Cascale"
            ],
            "certifications": [
                "BCI",
                "B Corp"
            ]
        }

    """
    return Response({
        'affiliations': ClaimAffiliation.objects.active_names(),
        'certifications': ClaimCertification.objects.active_names(),
    })
