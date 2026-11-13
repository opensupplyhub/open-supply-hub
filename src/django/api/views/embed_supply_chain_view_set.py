from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.viewsets import ModelViewSet

from ..models.embed_supply_chain import EmbedSupplyChain
from ..serializers.embed_supply_chain import EmbedSupplyChainSerializer
from .contributor.get_contributor import get_contributor

DELUXE_EMBED_LEVEL = 3


class EmbedSupplyChainViewSet(ModelViewSet):
    """
    A contributor's own supply chains for their embedded map. Only the
    contributor can see or change them here; visitors get the published
    ones through the contributor's embed config.
    """
    serializer_class = EmbedSupplyChainSerializer
    swagger_schema = None
    pagination_class = None

    def _contributor(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        contributor = get_contributor(self.request)
        if contributor.embed_level != DELUXE_EMBED_LEVEL:
            raise PermissionDenied(
                'Supply chains are part of the Embed Deluxe package.'
            )
        return contributor

    def get_queryset(self):
        return EmbedSupplyChain.objects.filter(
            contributor=self._contributor()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['contributor'] = self._contributor()
        return context

    def perform_create(self, serializer):
        serializer.save(contributor=self._contributor())
