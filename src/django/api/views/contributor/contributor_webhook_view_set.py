from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ...models import ContributorWebhook
from ...serializers import ContributorWebhookSerializer


class ContributorWebhookViewSet(CreateModelMixin,
                                DestroyModelMixin,
                                ListModelMixin,
                                UpdateModelMixin,
                                GenericViewSet):
    """
    Views for managing contributor webhooks
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ContributorWebhookSerializer
    swagger_schema = None

    def get_queryset(self):
        return (
            ContributorWebhook
            .objects
            .filter(contributor=self.request.user.contributor)
            .order_by('-created_at')
        )
