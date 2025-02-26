from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
        required=True,
    )
    max = serializers.IntegerField(
        min_value=1,
        required=True,
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

        min = data.get('min')
        max = data.get('max')
        errors = []

        if not min:
            errors.append({
                "field": "min",
                "detail":
                    "The min field is required!"
            })

        if not max:
            errors.append({
                "field": "max",
                "detail":
                    "The max field is required!"
            })

        if min and not isinstance(data.get('min'), int):
            errors.append({
                "field": "min",
                "detail":
                    "The min field must be an integer."
            })

        if max and not isinstance(data.get('max'), int):
            errors.append({
                "field": "max",
                "detail":
                    "The max field must be an integer."
            })

        if len(errors) > 0:
            raise serializers.ValidationError({"field": self.field_name,
                                               "errors": errors})

        return super().to_internal_value(data)
