from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from waffle import switch_is_active

from api.constants import FacilitiesQueryParams
from api.isic import parse_isic4_filter_values
from api.isic_taxonomy.constants import ISIC_TAXONOMY_SWITCH
from api.isic_taxonomy.crosswalk import LEVEL_PATTERNS
from api.taxonomy_counts import (
    compute_isic4_counts,
    compute_isic4_mapped_extra_count,
)
from api.view_response_cache import cache_view_response

TAXONOMY_COUNT_KINDS = ('isic4', 'isic4_mapped_extra')
# The response cache keys on every query param, so an unknown param would
# force a fresh full count; reject them instead.
TAXONOMY_COUNT_PARAMS = {
    'kind',
    'include_mapped',
    FacilitiesQueryParams.ISIC_4,
}

# Each distinct selection is its own cache entry and COUNT query, so the
# public endpoint only accepts well-formed codes and a bounded selection.
MAX_ISIC_SELECTIONS = 50


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
                    'level:code (e.g. section:C, class:0111). '
                    'isic4_mapped_extra returns {"count": N}, the number of '
                    'locations the isic_4 selection adds when mapped values '
                    'are included.'
                ),
            ),
            openapi.Parameter(
                'include_mapped',
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description=(
                    'isic4 only: also count values mapped from facility and '
                    'processing type.'
                ),
            ),
            openapi.Parameter(
                FacilitiesQueryParams.ISIC_4,
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description=(
                    'isic4_mapped_extra only: repeatable level:code '
                    'selection, as for GET /api/facilities/.'
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

        if kind == 'isic4_mapped_extra':
            parsed_isic_filters = parse_isic4_filter_values(
                request.query_params.getlist(FacilitiesQueryParams.ISIC_4)
            )
            if len(parsed_isic_filters) > MAX_ISIC_SELECTIONS:
                raise ValidationError({
                    FacilitiesQueryParams.ISIC_4: (
                        f'At most {MAX_ISIC_SELECTIONS} values are allowed.'
                    ),
                })
            invalid = [
                code for field_name, code in parsed_isic_filters
                if not LEVEL_PATTERNS[field_name].match(code)
            ]
            if invalid:
                raise ValidationError({
                    FacilitiesQueryParams.ISIC_4: (
                        f'Invalid ISIC codes: {", ".join(invalid)}.'
                    ),
                })
            return Response({
                'count': compute_isic4_mapped_extra_count(
                    parsed_isic_filters
                ),
            })

        include_mapped = request.query_params.get('include_mapped', 'false')
        if include_mapped not in ('true', 'false'):
            raise ValidationError({
                'include_mapped': 'Expected true or false.',
            })

        return Response(compute_isic4_counts(
            include_mapped=include_mapped == 'true',
        ))
