from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError
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

# The response cache keys on every query param, so a param a kind does not
# use, or a repeated one, would force a fresh count; reject them instead.
PARAMS_BY_KIND = {
    'isic4': {'kind', 'include_mapped'},
    'isic4_mapped_extra': {'kind', FacilitiesQueryParams.ISIC_4},
}
TAXONOMY_COUNT_KINDS = tuple(PARAMS_BY_KIND)
SINGLE_VALUE_PARAMS = ('kind', 'include_mapped')

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
        repeated = [
            param for param in SINGLE_VALUE_PARAMS
            if len(request.query_params.getlist(param)) > 1
        ]
        if repeated:
            raise ValidationError({
                param: 'Give this parameter once.' for param in repeated
            })

        kind = request.query_params.get('kind')
        if kind not in TAXONOMY_COUNT_KINDS:
            raise ValidationError({
                'kind': (
                    f'Invalid kind "{kind}". '
                    f'Expected one of: {", ".join(TAXONOMY_COUNT_KINDS)}.'
                ),
            })

        unknown = set(request.query_params) - PARAMS_BY_KIND[kind]
        if unknown:
            raise ValidationError({
                param: 'Unknown parameter.' for param in sorted(unknown)
            })

        # A 404 is not cached, so counts appear as soon as the switch is on.
        if not switch_is_active(ISIC_TAXONOMY_SWITCH):
            raise NotFound('ISIC is switched off.')

        if kind == 'isic4_mapped_extra':
            values = request.query_params.getlist(FacilitiesQueryParams.ISIC_4)
            parsed_isic_filters = parse_isic4_filter_values(values)
            if len(values) > MAX_ISIC_SELECTIONS:
                raise ValidationError({
                    FacilitiesQueryParams.ISIC_4: (
                        f'At most {MAX_ISIC_SELECTIONS} values are allowed.'
                    ),
                })
            # Every value must be a well-formed level:code; ignored junk
            # would still make a new cache entry.
            invalid = [
                code for field_name, code in parsed_isic_filters
                if not LEVEL_PATTERNS[field_name].match(code)
            ]
            if invalid or len(parsed_isic_filters) != len(values):
                raise ValidationError({
                    FacilitiesQueryParams.ISIC_4: (
                        'Expected level:code values such as class:1410.'
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
