import logging
from functools import wraps

from rest_framework.response import Response
from rest_framework import status

from api.views.v1.parameters_list import V1_PARAMETERS_LIST
from api.services.opensearch.search import OpenSearchServiceException
from api.constants import APIV1CommonErrorMessages, NON_FIELD_ERRORS_KEY

logger = logging.getLogger(__name__)


def serialize_params(serializer_class, query_params):
    flattened_query_params = {}
    for key, value in query_params.lists():
        # Convert deepObject params
        if key in [
            f'{V1_PARAMETERS_LIST.NUMBER_OF_WORKERS}[min]',
            f'{V1_PARAMETERS_LIST.NUMBER_OF_WORKERS}[max]',
            f'{V1_PARAMETERS_LIST.PERCENT_FEMALE_WORKERS}[min]',
            f'{V1_PARAMETERS_LIST.PERCENT_FEMALE_WORKERS}[max]',
            f'{V1_PARAMETERS_LIST.COORDINATES}[lat]',
            f'{V1_PARAMETERS_LIST.COORDINATES}[lng]',
            f'{V1_PARAMETERS_LIST.SEARCH_AFTER}[id]',
            f'{V1_PARAMETERS_LIST.SEARCH_AFTER}[value]'
        ]:
            new_key = key.replace(']', '').replace('[', '_')
            flattened_query_params[new_key] = value[0]
        # Prepare only single params
        elif key in [
            V1_PARAMETERS_LIST.ADDRESS,
            V1_PARAMETERS_LIST.DESCRIPTION,
            V1_PARAMETERS_LIST.SORT_BY,
            V1_PARAMETERS_LIST.ORDER_BY,
            V1_PARAMETERS_LIST.SIZE,
            V1_PARAMETERS_LIST.DATE_GTE,
            V1_PARAMETERS_LIST.DATE_LT,
            V1_PARAMETERS_LIST.PRECISION,
            V1_PARAMETERS_LIST.AGGREGATION,
        ]:
            flattened_query_params[key] = value[0]
        else:
            flattened_query_params[key] = value

    params = serializer_class(data=flattened_query_params)

    if not params.is_valid():
        error_response = {'detail': None, 'errors': []}
        # Handle common validation errors.
        if 'detail' not in params.errors and 'errors' not in params.errors:
            error_response['detail'] = \
                APIV1CommonErrorMessages.COMMON_REQ_QUERY_ERROR
            for field, error_list in params.errors.items():
                error_response['errors'].append({
                    'field': field,
                    'detail': error_list[0].capitalize()
                })

        # Handle errors that come from serializers
        detail_errors = params.errors.get('detail')
        if detail_errors:
            error_response['detail'] = detail_errors[0].capitalize()
        if 'detail' in params.errors and 'errors' in params.errors:
            for error_item in params.errors.get('errors', []):
                error_response['errors'].append({
                    'field': error_item.get('field', ''),
                    'detail': error_item.get('detail', '').capitalize()
                })

        return None, error_response

    return params.validated_data, None


def handle_value_error(e):
    logger.error(f'Error processing request: {e}')
    return Response(
        {
            "detail": APIV1CommonErrorMessages.COMMON_REQ_QUERY_ERROR,
            "errors": [
                {
                    "field": NON_FIELD_ERRORS_KEY,
                    "detail": (
                        "There was a problem processing your request. "
                        "Please check your input."
                    )
                }
            ]
        },
        status=status.HTTP_400_BAD_REQUEST
    )


def handle_opensearch_exception(e):
    logger.error(f'Internal server error: {e}')
    return Response(
        {
            "detail": f"{e}"
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def handle_errors_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except ValueError as e:
            return handle_value_error(e)
        except OpenSearchServiceException as e:
            return handle_opensearch_exception(e)
    return _wrapped_view


def create_error_detail(
        field,
        detail,
        general_detail="The request path parameter is invalid."
):
    return {
        "detail": general_detail,
        "errors": [
            {
                "field": field,
                "detail": detail,
            }
        ]
    }
