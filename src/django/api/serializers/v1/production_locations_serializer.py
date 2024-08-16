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
    percent_of_female_workers import PercentOfFemaleWorkersValidator
from api.serializers.v1.opensearch_common_validators. \
    coordinates_validator import CoordinatesValidator
from api.views.v1.utils import COMMON_ERROR_MESSAGE


class ProductionLocationsSerializer(Serializer):
    # These params are checking considering serialize_params output
    size = IntegerField(required=False)
    number_of_workers_min = IntegerField(required=False)
    number_of_workers_max = IntegerField(required=False)
    percent_female_workers_min = FloatField(required=False)
    percent_female_workers_max = FloatField(required=False)
    coordinates_lat = FloatField(required=False)
    coordinates_lon = FloatField(required=False)
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
            # TODO: Pass error msg to the Rollbar here
            raise ValidationError({
                "message": COMMON_ERROR_MESSAGE,
                "errors": errors
            })

        return data
