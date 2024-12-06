from rest_framework.serializers import (
    CharField,
    ChoiceField,
    DateField,
    IntegerField,
    ListField,
    Serializer,
    ValidationError
)
from api.serializers.v1.opensearch_common_validators.size_validator \
    import SizeValidator
from api.serializers.v1.opensearch_common_validators.request_type_validator \
    import RequestTypeValidator
from api.serializers.v1.opensearch_common_validators.status_validator \
    import StatusValidator
from api.serializers.v1.opensearch_common_validators.source_validator \
    import SourceValidator
from api.serializers.v1.opensearch_common_validators.moderation_id_validator \
    import ModerationIdValidator
from api.serializers.v1.opensearch_error_list_builder  \
    import OpenSearchErrorListBuilder
from api.serializers.v1.opensearch_common_validators. \
    countries_validator import CountryValidator
from api.serializers.v1.opensearch_common_validators. \
    date_range_validator import DateRangeValidator
from api.constants import APIV1CommonErrorMessages


class ModerationEventsSerializer(Serializer):
    # These params are checking considering serialize_params output
    size = IntegerField(required=False)
    search_after_id = CharField(required=False)
    search_after_value = CharField(required=False)
    country = ListField(
        child=CharField(required=False),
        required=False
    )
    moderation_id = ListField(
        child=CharField(required=False),
        required=False
    )
    date_gte = DateField(input_formats=['%Y-%m-%d'], required=False)
    date_lt = DateField(input_formats=['%Y-%m-%d'], required=False)
    request_type = ListField(
        child=CharField(required=False),
        required=False
    )
    source = ListField(
        child=CharField(required=False),
        required=False
    )
    status = ListField(
        child=CharField(required=False),
        required=False
    )
    sort_by = ChoiceField(
        choices=[
            'created_at',
            'status_change_date',
            'updated_at',
            'contributor_id',
            'contributor_name',
            'country',
            'name',
            'address',
            'source',
            'status',
        ],
        required=False
    )
    order_by = ChoiceField(
        choices=['asc', 'desc'],
        required=False
    )

    def validate(self, data):
        validators = [
            SizeValidator(),
            CountryValidator(),
            DateRangeValidator(),
            RequestTypeValidator(),
            StatusValidator(),
            SourceValidator(),
            ModerationIdValidator()
        ]

        error_list_builder = OpenSearchErrorListBuilder(validators)
        errors = error_list_builder.build_error_list(data)

        if errors:
            # [OSDEV-1441] Pass error msg to the Rollbar here
            raise ValidationError({
                "detail": APIV1CommonErrorMessages.COMMON_REQ_QUERY_ERROR,
                "errors": errors
            })

        return data
