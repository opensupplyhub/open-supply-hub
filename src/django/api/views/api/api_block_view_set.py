from rest_framework.mixins import (
  ListModelMixin,
  RetrieveModelMixin,
  UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from ...models import ApiBlock
from ...serializers.api_block import ApiBlockSerializer
from ...permissions import IsSuperuser


class ApiBlockViewSet(ListModelMixin,
                      RetrieveModelMixin,
                      UpdateModelMixin,
                      GenericViewSet):
    """
    Get ApiBlocks.
    """
    queryset = ApiBlock.objects.all()
    serializer_class = ApiBlockSerializer
    permission_classes = [IsSuperuser]
    swagger_schema = None
    pagination_class = None
    throttle_classes = []
