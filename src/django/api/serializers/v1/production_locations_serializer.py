from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


class ProductionLocationsSerializer(serializers.Serializer):

    number_of_workers_min = serializers.IntegerField(required=False)
    number_of_workers_max = serializers.IntegerField(required=False)
    percent_female_workers = serializers.FloatField(required=False)
    coordinates = serializers.JSONField(required=False)

    def validate(self, data):
        errors = []

        min_value = data.get('number_of_workers_min')
        max_value = data.get('number_of_workers_max')

        if ((min_value is not None and max_value is None) or
                (min_value is None and max_value is not None)):
            errors.append({
                "field": "number_of_workers",
                "message": (
                    "The value must be a valid object with `min` and `max` "
                    "properties."
                )
            })

        if (min_value is not None and max_value is not None and
                min_value > max_value):
            errors.append({
                "field": "number_of_workers",
                "message": (
                    "Minimum value must be less than or equal "
                    "to maximum value."
                )
            })

        if errors:
            raise serializers.ValidationError({
                "message": "The request query is invalid.",
                "errors": errors
            })

        return data
