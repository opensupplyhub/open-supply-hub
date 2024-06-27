from rest_framework.serializers import (
    ChoiceField,
    Serializer,
)
from ...models import FacilityClaim


class FacilityClaimListQueryParamsSerializer(Serializer):
    status = ChoiceField(choices=[FacilityClaim.PENDING, FacilityClaim.APPROVED,
                                  FacilityClaim.REVOKED, FacilityClaim.DENIED],
                         required=False)
