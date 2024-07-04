from rest_framework.serializers import (
    ChoiceField,
    ListField,
    Serializer,
    CharField,
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
    countries = ListField(
        child=CharField(required=False),
        required=False,
    )
