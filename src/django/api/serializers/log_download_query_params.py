from django.forms import ValidationError
from rest_framework.serializers import (
    CharField,
    IntegerField,
    Serializer,
)


class LogDownloadQueryParamsSerializer(Serializer):
    path = CharField(required=True)
    record_count = IntegerField(required=True)

    def validate_path(self, value):
        max_length = 4096
        if len(value) > max_length:
            raise ValidationError(
                f"Path length must not exceed "
                f"{max_length} characters."
            )
        return value
