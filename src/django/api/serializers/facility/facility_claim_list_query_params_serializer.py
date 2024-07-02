from rest_framework.serializers import (
    ChoiceField,
    ListField,
    Serializer,
)
from ...models import FacilityClaim


class FacilityClaimListQueryParamsSerializer(Serializer):
    statuses = ListField(
        child=ChoiceField(choices=[
            FacilityClaim.PENDING,
            FacilityClaim.APPROVED,
            FacilityClaim.REVOKED,
            FacilityClaim.DENIED
        ]),
        required=False)
