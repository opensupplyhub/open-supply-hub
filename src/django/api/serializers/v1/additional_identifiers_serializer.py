from rest_framework import serializers


class AdditionalIdentifiersSerializer(serializers.Serializer):
    rba_id = serializers.CharField(required=False)
    duns_id = serializers.CharField(required=False)
    lei_id = serializers.CharField(required=False)

    def validate(self, data):
        errors = []

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data
