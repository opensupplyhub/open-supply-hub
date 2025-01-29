from rest_framework.serializers import (
    CharField,
    ChoiceField,
    FloatField,
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
    number_of_workers_validator import NumberOfWorkersValidator
from api.serializers.v1.opensearch_common_validators. \
    percent_of_female_workers_validator import PercentOfFemaleWorkersValidator
from api.serializers.v1.opensearch_common_validators. \
    coordinates_validator import CoordinatesValidator
from api.constants import APIV1CommonErrorMessages


class ProductionLocationsSerializer(Serializer):
    # These params are checking considering serialize_params output
    size = IntegerField(required=False)
    address = CharField(required=False)
    description = CharField(required=False)
    number_of_workers_min = IntegerField(required=False)
    number_of_workers_max = IntegerField(required=False)
    percent_female_workers_min = FloatField(required=False)
    percent_female_workers_max = FloatField(required=False)
    search_after_id = CharField(required=False)
    search_after_value = CharField(required=False)
    coordinates_lat = FloatField(required=False)
    coordinates_lng = FloatField(required=False)
    country = ListField(
        child=CharField(required=False),
        required=False
    )
    sort_by = ChoiceField(
        choices=['name', 'address'],
        required=False
    )
    order_by = ChoiceField(
        choices=['asc', 'desc'],
        required=False
    )
    aggregation = ChoiceField(
        choices=['geohex_grid'],
        required=False,
    )
    geohex_grid_precision = IntegerField(
        min_value=0,
        max_value=15,
        required=False,
    )

    def validate(self, data):
        validators = [
            SizeValidator(),
            NumberOfWorkersValidator(),
            PercentOfFemaleWorkersValidator(),
            CoordinatesValidator(),
            CountryValidator(),
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
