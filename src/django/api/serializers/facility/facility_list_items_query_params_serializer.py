from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CharField,
    ListField,
    Serializer,
)
from ...models import FacilityListItem


class FacilityListItemsQueryParamsSerializer(Serializer):
    search = CharField(required=False)
    status = ListField(
        child=CharField(required=False),
        required=False,
    )

    def validate_status(self, value):
        valid_statuses = ([c[0] for c in FacilityListItem.STATUS_CHOICES]
                          + [FacilityListItem.NEW_FACILITY,
                             FacilityListItem.REMOVED])
        for item in value:
            if item not in valid_statuses:
                statuses_string = ', '.join(valid_statuses)
                raise ValidationError((
                    f"{item} is not a valid status."
                    f"Must be one of {statuses_string}"
                ))
