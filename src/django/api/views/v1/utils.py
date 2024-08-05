from rest_framework.response import Response
from rest_framework import status
import logging
logger = logging.getLogger(__name__)


def serialize_params(serializer_class, query_params):
    flattened_query_params = {
        key.replace(']', '').replace('[', '_'): value
        for key, value in query_params.items()
    }

    params = serializer_class(data=flattened_query_params)
    if not params.is_valid():
        error_response = {
            'message': None,
            'errors': []
        }

        error_response['message'] = (
            params.errors.get('message')[0].title()
        )

        for error_item in params.errors.get('errors', []):
            field = str(error_item.get('field', '')).title()
            message = str(error_item.get('message', '')).title()
            error_response['errors'].append({
                'field': field,
                'message': message
            })

        return None, error_response

    return params.validated_data, None


def handle_value_error(e):
    logger.error(f'Error processing request: {e}')
    return Response(
        {
            "message": "The request query is invalid.",
            "errors": [
                {
                    "field": "general",
                    "message": (
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
            "message": f"{e}"
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
