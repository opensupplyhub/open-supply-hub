from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from waffle import switch_is_active

from api.models.facility.claim_campaign import ClaimCampaign
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.facility.claim_campaign_serializer import (
    ClaimCampaignSerializer,
)


class ClaimCampaignViewSet(ListModelMixin, GenericViewSet):
    """
    Read-only list of the requesting user's own claim campaigns with
    per-supplier claim statuses. Statuses expose only what is already
    public (unclaimed / pending / claimed).
    """

    serializer_class = ClaimCampaignSerializer
    permission_classes = (IsRegisteredAndConfirmed,)
    pagination_class = None

    def get_queryset(self):
        if not switch_is_active('claim_campaigns'):
            raise NotFound()

        contributor = getattr(self.request.user, 'contributor', None)
        if contributor is None:
            return ClaimCampaign.objects.none()

        return ClaimCampaign.objects.filter(
            contributor=contributor,
        ).order_by('-created_at')
