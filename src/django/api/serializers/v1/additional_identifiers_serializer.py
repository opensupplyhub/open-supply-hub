from rest_framework import serializers


class AdditionalIdentifiersSerializer(serializers.Serializer):
    rba_id = serializers.CharField(required=False)
    duns_id = serializers.CharField(required=False)
    lei_id = serializers.CharField(required=False)

    def validate(self, data):
        errors = []

        rba_id = data.get('rba_id') if 'rba_id' in data else None
        duns_id = data.get('duns_id') if 'duns_id' in data else None
        lei_id = data.get('lei_id') if 'lei_id' in data else None

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data
