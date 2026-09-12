from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListField,
    Serializer,
)

from api.services.processing_type_search import (
    DEFAULT_SUGGESTION_LIMIT,
    MAX_SUGGESTION_LIMIT,
)


class ProcessingTypeSuggestionsQueryParamsSerializer(Serializer):
    q = CharField(required=False, allow_blank=True, default='')
    facility_type = ListField(
        child=CharField(allow_blank=True),
        required=False,
        default=list,
    )
    limit = IntegerField(
        required=False,
        default=DEFAULT_SUGGESTION_LIMIT,
        min_value=0,
        allow_null=True,
    )

    def validate_limit(self, value):
        """Preserve the endpoint contract by capping oversized limits."""
        if value is None:
            return DEFAULT_SUGGESTION_LIMIT
        return min(value, MAX_SUGGESTION_LIMIT)
