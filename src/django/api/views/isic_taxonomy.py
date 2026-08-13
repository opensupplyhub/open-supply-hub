from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.isic_taxonomy.content import (
    IsicTaxonomyNotAvailable,
    load_isic4_taxonomy_content,
)


class IsicTaxonomyView(APIView):
    throttle_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            'Return the active ISIC Rev 4 taxonomy tree as JSON. '
            'Content is loaded from the private files bucket by Django '
            'and cached server-side for one hour; cache is invalidated '
            'on publish or enable/disable.'
        ),
    )
    def get(self, request):
        try:
            return Response(load_isic4_taxonomy_content())
        except IsicTaxonomyNotAvailable:
            raise NotFound('ISIC taxonomy is not available.')
