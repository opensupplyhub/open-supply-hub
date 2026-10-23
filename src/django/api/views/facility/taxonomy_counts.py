from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from waffle import switch_is_active

from api.isic_taxonomy.constants import ISIC_TAXONOMY_SWITCH
from api.taxonomy_counts import compute_isic4_counts
from api.view_response_cache import cache_view_response

TAXONOMY_COUNT_KINDS = ('isic4',)
# The response cache keys on every query param, so an unknown param would
# force a fresh full count; reject them instead.
TAXONOMY_COUNT_PARAMS = {'kind'}


class TaxonomyCountsView(APIView):
    throttle_classes = []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'kind',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                enum=list(TAXONOMY_COUNT_KINDS),
                description=(
                    'Taxonomy to count. isic4 returns counts keyed by '
                    'level:code (e.g. section:C, class:0111).'
                ),
            ),
        ],
        operation_description=(
            'Return facility counts grouped by ISIC taxonomy node for the '
            'main search UI.'
        ),
    )
    @cache_view_response('taxonomy_counts')
    def get(self, request):
        unknown = set(request.query_params) - TAXONOMY_COUNT_PARAMS
        if unknown:
            raise ValidationError({
                param: 'Unknown parameter.' for param in sorted(unknown)
            })

        kind = request.query_params.get('kind')
        if kind not in TAXONOMY_COUNT_KINDS:
            raise ValidationError({
                'kind': (
                    f'Invalid kind "{kind}". '
                    f'Expected one of: {", ".join(TAXONOMY_COUNT_KINDS)}.'
                ),
            })

        if not switch_is_active(ISIC_TAXONOMY_SWITCH):
            return Response({})

        return Response(compute_isic4_counts())
