from rest_framework.serializers import (
    CharField,
    IntegerField,
    Serializer,
)


class LogDownloadQueryParamsSerializer(Serializer):
    path = CharField(required=True)
    record_count = IntegerField(required=True)
