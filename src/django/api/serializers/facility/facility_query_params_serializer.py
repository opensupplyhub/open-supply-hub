from rest_framework.serializers import (
    BooleanField,
    CharField,
    IntegerField,
    ListField,
    Serializer,
    ValidationError,
)


DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL = (
    'detail_provenance_data can only be used together with detail=true.'
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
    # OSDEV-3751: fill each extended-field entry's `provenance` with the
    # data of the FacilityListItem it came from. Only meaningful with
    # `detail`, since extended fields are left out of the response otherwise.
    detail_provenance_data = BooleanField(default=False, required=False)
    number_of_public_contributors = BooleanField(default=False, required=False)
    sort_by = CharField(default=None, required=False)
    embed = IntegerField(default=0, required=False)

    def validate(self, attrs):
        if attrs.get('detail_provenance_data') and not attrs.get('detail'):
            raise ValidationError({
                'detail_provenance_data': [
                    DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL
                ],
            })
        return attrs
