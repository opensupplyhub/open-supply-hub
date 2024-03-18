from rest_framework.serializers import (
    BooleanField,
    CharField,
    IntegerField,
    ListField,
    Serializer,
)


class FacilityQueryParamsSerializer(Serializer):
    name = CharField(required=False)
    contributors = ListField(
        default=list,
        child=IntegerField(required=False),
        required=False,
    )
    lists = ListField(
        child=IntegerField(required=False),
        required=False,
    )
    contributor_types = ListField(
        child=CharField(required=False),
        required=False,
    )
    countries = ListField(
        child=CharField(required=False),
        required=False,
    )
    boundary = CharField(required=False)
    detail = BooleanField(default=False, required=False)
    number_of_public_contributors = BooleanField(default=False, required=False)
    sort_by = CharField(required=False)
    embed = IntegerField(default=0, required=False)
