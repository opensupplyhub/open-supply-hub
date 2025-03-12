from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
    )
    max = serializers.IntegerField(
        min_value=1,
    )

    def validate(self, data):
        min_value = data.get('min')
        max_value = data.get('max')

        if (
            min_value is not None
            and max_value is not None
            and min_value > max_value
        ):
            raise serializers.ValidationError(
                {"min": ('The min field must be less than or equal'
                         ' to the max field.')}
            )

        return data

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
              "Invalid data. Expected a dictionary(object).")

        min_value = data.get('min')
        max_value = data.get('max')
        errors = []

        if min_value is None:
            errors.append({
                "field": "min",
                "detail":
                    "The min field is required!"
            })

        if max_value is None:
            errors.append({
                "field": "max",
                "detail":
                    "The max field is required!"
            })

        if min_value is not None and not isinstance(min_value, int):
            errors.append({
                "field": "min",
                "detail":
                    "The min field must be an integer."
            })

        if max_value is not None and not isinstance(max_value, int):
            errors.append({
                "field": "max",
                "detail":
                    "The max field must be an integer."
            })

        if len(errors) > 0:
            raise serializers.ValidationError({"field": self.field_name,
                                               "errors": errors})

        return super().to_internal_value(data)
