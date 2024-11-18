from rest_framework.serializers import (
    CharField,
    Serializer,
)


class ProductionLocationModerationSourceSerializer(Serializer):
    source = CharField(required=True)
