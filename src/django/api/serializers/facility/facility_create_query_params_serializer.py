from rest_framework.serializers import (
    BooleanField,
    Serializer,
)


class FacilityCreateQueryParamsSerializer(Serializer):
    create = BooleanField(default=True, required=False)
    public = BooleanField(default=True, required=False)
    textonlyfallback = BooleanField(default=False, required=False)
