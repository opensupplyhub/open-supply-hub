from rest_framework import serializers
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


class ProductionLocationsSerializer(serializers.Serializer):

    size = serializers.IntegerField(required=False)
    number_of_workers_min = serializers.IntegerField(required=False)
    number_of_workers_max = serializers.IntegerField(required=False)
    percent_female_workers_min = serializers.FloatField(required=False)
    percent_female_workers_max = serializers.FloatField(required=False)
    coordinates_lat = serializers.FloatField(required=False)
    coordinates_lon = serializers.FloatField(required=False)
    country = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate(self, data):
        validators = [
            NumberOfWorkersValidator(),
            PercentOfFemaleWorkersValidator(),
            CoordinatesValidator(),
            CountryValidator(),
        ]

        error_list_builder = OpenSearchErrorListBuilder(validators)
        errors = error_list_builder.build_error_list(data)

        if errors:
            raise serializers.ValidationError({
                "message": COMMON_ERROR_MESSAGE,
                "errors": errors
            })

        return data
