from rest_framework.response import Response
from rest_framework import status
import logging
logger = logging.getLogger(__name__)


COMMON_ERROR_MESSAGE = 'The request query is invalid.'


def is_deep_object_url_param(s):
    return '[' in s and ']' in s


def can_be_converted_to_int_url_param(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def serialize_params(serializer_class, query_params):
    flattened_query_params = {}
    for key, value in query_params.lists():
        new_key = key.replace(']', '').replace('[', '_')
        if len(value) == 1 and is_deep_object_url_param(key):
            flattened_query_params[new_key] = value[0]
        else:
            flattened_query_params[new_key] = (
                int(value[0]) if can_be_converted_to_int_url_param(value[0])
                else value[0]
            )

    params = serializer_class(data=flattened_query_params)

    if not params.is_valid():
        error_response = {'message': None, 'errors': []}

        '''
        Handle common validation errors.
        If there is at least one validation errors,
        errors from serializers won't appear.
        '''
        if 'message' not in params.errors and 'errors' not in params.errors:
            error_response['message'] = COMMON_ERROR_MESSAGE
            for field, error_list in params.errors.items():
                error_response['errors'].append({
                    'field': field,
                    'message': error_list[0].title()
                })

        # Handle errors that come from serializers
        message_errors = params.errors.get('message')
        if message_errors:
            error_response['message'] = message_errors[0].title()
        if 'message' in params.errors and 'errors' in params.errors:
            for error_item in params.errors.get('errors', []):
                error_response['errors'].append({
                    'field': error_item.get('field', '').title(),
                    'message': error_item.get('message', '').title()
                })

        logger.info(f'### Error is {params.errors}')

        return None, error_response

    return params.validated_data, None


def handle_value_error(e):
    logger.error(f'Error processing request: {e}')
    return Response(
        {
            "message": COMMON_ERROR_MESSAGE,
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
