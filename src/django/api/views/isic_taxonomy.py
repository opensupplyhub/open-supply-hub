from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from waffle import switch_is_active

from api.isic_taxonomy import revisions
from api.isic_taxonomy.constants import ISIC_TAXONOMY_SWITCH

# The UN files only change with a deploy.
ISIC_TAXONOMY_CACHE_CONTROL = 'public, max-age=3600'


class IsicTaxonomyView(APIView):
    throttle_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            'Return the ISIC Rev 4 and Rev 5 categories the search field '
            'offers, one entry per level and title, with the code it has in '
            'each revision. From the UN files shipped with the code.'
        ),
    )
    def get(self, request):
        if not switch_is_active(ISIC_TAXONOMY_SWITCH):
            raise NotFound('ISIC is switched off.')
        response = Response({'entries': revisions.entries()})
        response['Cache-Control'] = ISIC_TAXONOMY_CACHE_CONTROL
        return response
