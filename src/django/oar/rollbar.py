import rollbar
import sys
from django.conf import settings


def report_error_to_rollbar(
        request=None,
        message=None,
        auth=None,
        file=None,
        extra_data=None,
        exception=None):
    ROLLBAR = getattr(settings, 'ROLLBAR', {})
    if ROLLBAR:
        data = extra_data or {}
        contributor_id_msg = ''
        is_api_user_msg = ''
        if request:
            data['fingerprint'] = data['user_id'] = \
                getattr(request.user, 'id', None)
            data['contributor_id'] = getattr(getattr(
                request.user, 'contributor', None), 'id', None)
            data['is_api_user'] = getattr(request.user, 'has_groups', False)
            if data["contributor_id"]:
                contributor_id_msg = (
                    f' (contributor id {data["contributor_id"]})'
                )
            if data['is_api_user']:
                is_api_user_msg = 'API '
            if file:
                data['file_name'] = file.name
            if auth:
                data['auth'] = auth
        if message:
            rollbar.report_message(message, level='error', extra_data=data)
        elif exception:
            modified_message = (
                f"{is_api_user_msg}User error{contributor_id_msg}: {exception}"
            )
            new_exception = Exception(modified_message)
            rollbar.report_exc_info(
                (type(new_exception), new_exception, sys.exc_info()[2]),
                extra_data=data
            )
        else:
            rollbar.report_exc_info(sys.exc_info(), extra_data=data)
