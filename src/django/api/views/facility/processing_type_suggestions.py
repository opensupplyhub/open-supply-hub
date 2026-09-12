from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.facility \
    .processing_type_suggestions_query_params_serializer import (
        ProcessingTypeSuggestionsQueryParamsSerializer,
    )
from api.services.processing_type_search import (
    DEFAULT_SUGGESTION_LIMIT,
    MAX_SUGGESTION_LIMIT,
    ProcessingTypeSearch,
)
from api.view_response_cache import cache_view_response

QUERY_PARAM = 'q'
FACILITY_TYPE_PARAM = 'facility_type'
LIMIT_PARAM = 'limit'


class ProcessingTypeSuggestionsView(APIView):
    # The typeahead fires on every keystroke past the client-side minimum
    # length, so it is exempt from the burst throttle like the other search
    # support endpoints.
    throttle_classes = []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                QUERY_PARAM,
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description=(
                    'Text to match against processing type values, '
                    'case- and accent-insensitively. When omitted, positive-'
                    'count results split slots evenly between taxonomy and '
                    'contributor values, with taxonomy receiving the odd '
                    'slot and either group backfilling unused slots.'
                ),
            ),
            openapi.Parameter(
                FACILITY_TYPE_PARAM,
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description=(
                    'Facility type to rank suggestions by. May be repeated. '
                    'Values whose facility types are not selected are '
                    'flagged with dim rather than being removed.'
                ),
            ),
            openapi.Parameter(
                LIMIT_PARAM,
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                default=DEFAULT_SUGGESTION_LIMIT,
                description=(
                    'Maximum number of suggestions to return. Values above '
                    f'{MAX_SUGGESTION_LIMIT} are capped at '
                    f'{MAX_SUGGESTION_LIMIT}.'
                ),
            ),
        ],
        operation_description=(
            'Return ranked processing type suggestions for the search '
            'filter typeahead. Suggestions cover both the Apparel taxonomy '
            'and contributor-submitted values that are not part of it yet, '
            'each with the number of locations carrying it. Responses are '
            'cached per set of query parameters. Zero-count taxonomy values '
            'remain available to typed queries but are omitted when the '
            'query is empty.'
        ),
    )
    @cache_view_response('processing_type_suggestions')
    def get(self, request):
        """
        ## Sample Response

            [
                {
                    "value": "DYEING",
                    "label": "DYEING",
                    "count": 1204,
                    "in_taxonomy": true,
                    "facility_types": [
                        "Printing, Product Dyeing and Laundering"
                    ],
                    "dim": false
                },
                {
                    "value": "yarn dyeing",
                    "label": "yarn dyeing",
                    "count": 37,
                    "in_taxonomy": false,
                    "facility_types": [],
                    "dim": true
                }
            ]

        """
        params = ProcessingTypeSuggestionsQueryParamsSerializer(
            data=request.query_params,
        )
        params.is_valid(raise_exception=True)

        search = ProcessingTypeSearch(
            query=params.validated_data[QUERY_PARAM],
            facility_types=params.validated_data[FACILITY_TYPE_PARAM],
            limit=params.validated_data[LIMIT_PARAM],
        )
        return Response(search.build_suggestions())
