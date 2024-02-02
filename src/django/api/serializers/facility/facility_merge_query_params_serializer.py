from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CharField,
    Serializer,
)

from ...models import Facility


class FacilityMergeQueryParamsSerializer(Serializer):
    target = CharField(required=True)
    merge = CharField(required=True)

    def validate_target(self, target_id):
        if not Facility.objects.filter(id=target_id).exists():
            raise ValidationError(
                f'Facility {target_id} does not exist.')

    def validate_merge(self, merge_id):
        if not Facility.objects.filter(id=merge_id).exists():
            raise ValidationError(
                f'Facility {merge_id} does not exist.')
