import rollbar
import sys
from django.conf import settings

def report_error_to_rollbar(request=None, message=None, auth=None, file=None, extra_data=None, exception=None):
    ROLLBAR = getattr(settings, 'ROLLBAR', {})
    if ROLLBAR:
        data = extra_data or {}
        contributorIdMsg = ''
        isApiUserMsg = ''
        if request:
            data['user_id'] = getattr(request.user, 'id', None)
            data['contributor_id'] = getattr(getattr(request.user, 'contributor', None), 'id', None)
            data['is_api_user'] = getattr(request.user, 'has_groups', False)
            if data["contributor_id"]:
                contributorIdMsg = f' (contributor id {data["contributor_id"]})'
            if data['is_api_user']:
                isApiUserMsg = 'API '
            if file:
                data['file_name'] = file.name
            if auth:
                data['auth'] = auth
        if message:
            rollbar.report_message(message, level='error', extra_data=data)
        elif exception:
            modified_message = f'{isApiUserMsg}User error{contributorIdMsg}: {exception}'
            new_exception = Exception(modified_message)
            rollbar.report_exc_info((type(new_exception), new_exception, sys.exc_info()[2]), extra_data=data)
        else:
            rollbar.report_exc_info(sys.exc_info(), extra_data=data)

