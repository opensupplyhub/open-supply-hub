from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from api.models.facility.claims_reason import ClaimsReason
from api.serializers.facility.claims_reason_serializer import ClaimsReasonSerializer


@permission_classes([IsAuthenticated])
class ClaimsReasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for fetching active claims reasons.
    Used to populate the dropdown in claim forms.
    """
    serializer_class = ClaimsReasonSerializer
    
    def get_queryset(self):
        return ClaimsReason.objects.filter(is_active=True)