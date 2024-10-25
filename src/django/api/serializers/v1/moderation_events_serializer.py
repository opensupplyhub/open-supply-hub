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
from api.serializers.v1.opensearch_error_list_builder  \
    import OpenSearchErrorListBuilder
from api.serializers.v1.opensearch_common_validators. \
    countries_validator import CountryValidator
from api.serializers.v1.opensearch_common_validators. \
    date_range_validator import DateRangeValidator
from api.views.v1.utils import COMMON_ERROR_MESSAGE


class ModerationEventsSerializer(Serializer):
    # These params are checking considering serialize_params output
    size = IntegerField(required=False)
    country = ListField(
        child=CharField(required=False),
        required=False
    )
    contributor_id = IntegerField(required=False)
    os_id = CharField(required=False)
    # TODO: add possibility to pass lowercase values?
    request_type = ChoiceField(
        choices=['CREATE', 'UPDATE', 'CLAIM'],
        required=False
    )
    source = ChoiceField(
        choices=['API', 'SLC'],
        required=False
    )
    status = ChoiceField(
        choices=['PENDING', 'RESOLVED'],
        required=False
    )
    moderation_id = CharField(required=False)
    data_dte = DateField(default='', required=False)
    data_lt = DateField(default='', required=False)
    sort_by = ChoiceField(
        choices=['name', 'address'],
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
        ]

        error_list_builder = OpenSearchErrorListBuilder(validators)
        errors = error_list_builder.build_error_list(data)

        if errors:
            # TODO: Pass error msg to the Rollbar here
            raise ValidationError({
                "message": COMMON_ERROR_MESSAGE,
                "errors": errors
            })

        return data
