from rest_framework.serializers import (
    IntegerField,
    ListField,
    Serializer,
)


class ContributorListQueryParamsSerializer(Serializer):
    contributors = ListField(
        child=IntegerField(required=True),
        required=False,
        allow_empty=False
    )
