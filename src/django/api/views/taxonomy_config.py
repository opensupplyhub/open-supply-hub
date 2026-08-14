from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.isic_taxonomy.runtime_config import (
    TAXONOMY_CONFIG_BROWSER_CACHE_CONTROL,
    get_taxonomy_config,
)


class TaxonomyConfigView(APIView):
    throttle_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            'Return runtime taxonomy configuration for the search UI. '
            'Responses are cached for 60 seconds server-side.'
        ),
    )
    def get(self, request):
        response = Response(get_taxonomy_config())
        response['Cache-Control'] = TAXONOMY_CONFIG_BROWSER_CACHE_CONTROL
        return response
