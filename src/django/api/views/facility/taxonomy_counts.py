from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.taxonomy_counts import (
    compute_isic4_counts,
    get_facility_processing_counts,
)
from api.view_response_cache import cache_view_response

TAXONOMY_COUNT_KINDS = ('facility_processing', 'isic4')


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
                    'Taxonomy to count. '
                    'facility_processing returns counts keyed by '
                    'facility_type:label or processing_type:label. '
                    'isic4 returns counts keyed by '
                    'level:code (e.g. section:C, class:0111).'
                ),
            ),
        ],
        operation_description=(
            'Return facility counts grouped by taxonomy node for the main '
            'search UI. facility_processing responses are cached for one '
            'hour; isic4 responses use the default view cache TTL.'
        ),
    )
    @cache_view_response('taxonomy_counts')
    def get(self, request):
        kind = request.query_params.get('kind')
        if kind not in TAXONOMY_COUNT_KINDS:
            raise ValidationError({
                'kind': (
                    f'Invalid kind "{kind}". '
                    f'Expected one of: {", ".join(TAXONOMY_COUNT_KINDS)}.'
                ),
            })

        if kind == 'facility_processing':
            return Response(get_facility_processing_counts())

        return Response(compute_isic4_counts())
