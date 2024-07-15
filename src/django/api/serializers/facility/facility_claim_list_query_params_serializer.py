from api.constants import FacilityClaimStatuses
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
            FacilityClaimStatuses.PENDING,
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.REVOKED,
            FacilityClaimStatuses.DENIED
        ]),
        required=False)
    countries = ListField(
        child=CharField(required=False),
        required=False,
    )
