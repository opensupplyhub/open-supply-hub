from rest_framework import serializers


class NumberOfWorkersSerializer(serializers.Serializer):
    min = serializers.IntegerField(
        min_value=1,
        required=True)
    max = serializers.IntegerField(
        min_value=1,
        required=True)

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
                {"min": "Min must be less than Max."}
            )

        return data
