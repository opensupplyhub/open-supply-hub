from rest_framework.serializers import (
  ModelSerializer,
)
from ...models import FacilityClaimAttachments


class FacilityClaimAttachmentsSerializer(ModelSerializer):
    class Meta:
        model = FacilityClaimAttachments
        fields = ('file_name', 'claim_attachment')
