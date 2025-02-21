from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The min field is required!',
            'invalid': 'The min field must be an integer.'
        }
    )
    max = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The max field is required!',
            'invalid': 'The max field must be an integer.'
        }
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

    @staticmethod
    def validate_object(value):
        return isinstance(value, dict)
