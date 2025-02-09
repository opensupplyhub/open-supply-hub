from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The min field is required!',
        })
    max = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The max field is required!',
        })

    def validate(self, data):
        """Ensure min is less than max"""
        min_value = data.get('min')
        max_value = data.get('max')

        if (
            min_value is not None
            and max_value is not None
            and min_value >= max_value
        ):
            raise serializers.ValidationError(
                {"min": "The min field must be less than max filed."}
            )

        return data

    def validate_object(self):
        return isinstance(self, dict)
