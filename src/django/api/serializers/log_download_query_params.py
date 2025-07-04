from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CharField,
    IntegerField,
    Serializer,
)
from api.models.download_log import DownloadLog

from api.models.download_log import DownloadLog


class LogDownloadQueryParamsSerializer(Serializer):
    path = CharField(required=True)
    record_count = IntegerField(required=True)

    def validate_path(self, value):
        max_length = DownloadLog._meta.get_field('path').max_length
        if len(value) > max_length:
            raise ValidationError(
                f"Path length must not exceed "
                f"{max_length} characters."
            )
        return value
