from rest_framework.serializers import CharField, Serializer, ValidationError

from api.models.facility.facility import Facility
from api.os_id import validate_os_id


class UpdateProductionLocationSerializer(Serializer):
    os_id = CharField(required=True)

    def validate_os_id(self, value):

        if not validate_os_id(value, raise_on_invalid=False):
            raise ValidationError("The format of the os_id is invalid.")

        if not Facility.objects.filter(id=value).exists():
            raise ValidationError(
                "No production location found with the provided os_id."
            )

        return value
