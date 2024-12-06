from rest_framework.serializers import (
    IntegerField,
    Serializer
)


class FacilityGetListPageSerializer(Serializer):
    page = IntegerField(
        required=False,
        max_value=100,
        min_value=1
    )
