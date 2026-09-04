from rest_framework.serializers import (
  ModelSerializer,
)
from ...models import FacilityClaimAttachments


class FacilityClaimAttachmentsSerializer(ModelSerializer):
    # Deliberately excludes the claim_attachment file field: its URL
    # representation is a presigned S3 URL — a shareable bearer token.
    # Clients download attachments through the authorization-checked
    # download endpoint on FacilityClaimViewSet instead.
    class Meta:
        model = FacilityClaimAttachments
        fields = ('id', 'file_name', 'uploaded_at')
