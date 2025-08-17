from rest_framework import serializers
from api.models.facility.claims_reason import ClaimsReason


class ClaimsReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimsReason
        fields = ('id', 'text')