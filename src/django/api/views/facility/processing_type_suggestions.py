from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.processing_type_search import (
    DEFAULT_SUGGESTION_LIMIT,
    MAX_SUGGESTION_LIMIT,
    search_processing_types,
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
        return Response(search_processing_types(
            query=request.query_params.get(QUERY_PARAM, ''),
            facility_types=request.query_params.getlist(FACILITY_TYPE_PARAM),
            limit=self.__parse_limit(request.query_params.get(LIMIT_PARAM)),
        ))

    @staticmethod
    def __parse_limit(raw_limit):
        if raw_limit is None or raw_limit == '':
            return DEFAULT_SUGGESTION_LIMIT

        try:
            limit = int(raw_limit)
        except ValueError:
            raise ValidationError({
                LIMIT_PARAM: (
                    f'Invalid limit "{raw_limit}". Expected an integer '
                    f'between 0 and {MAX_SUGGESTION_LIMIT}.'
                ),
            })

        if limit < 0:
            raise ValidationError({
                LIMIT_PARAM: 'Invalid limit. Expected a positive integer.',
            })

        return limit
