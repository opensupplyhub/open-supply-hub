from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The min field is required!',
        }
    )
    max = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'The max field is required!',
        }
    )

    @staticmethod
    def validate_object(value):
        return isinstance(value, dict)
