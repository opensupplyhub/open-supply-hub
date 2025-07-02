import datetime
import json
import threading

import requests

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.db import connection

from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token

from django.http import HttpResponse

from api.models import RequestLog
from api.limits import get_api_block
from oar.rollbar import report_error_to_rollbar


class RequestLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        auth = None
        try:
            if request.user and request.user.is_authenticated:
                auth = get_authorization_header(request)
                if auth and auth.split()[0].lower() == 'token'.encode():
                    token = auth.split()[1].decode()
                    RequestLog.objects.create(
                        user=request.user,
                        token=token,
                        method=request.method,
                        path=request.get_full_path(),
                        response_code=response.status_code,
                    )
        except Exception as err:
            try:
                report_error_to_rollbar(
                    request=request,
                    auth=auth,
                    exception=err
                )
            except Exception:
                pass  # We don't want this logging middleware to fail a request

        return response


def get_token(request):
    auth_header = get_authorization_header(request).decode()
    if auth_header and auth_header.split()[0].lower() == 'token':
        try:
            return Token.objects.get(key=auth_header.split()[1])
        except Token.DoesNotExist:
            # This function is designed to be called as part middleware and may
            # execute before Django REST Framework has processed the token
            # auth. A non-existent (invalid) token will be handled by that
            # process, so at this point we just want to quietly return None
            # rather than raise.
            return None
    else:
        return None


def has_active_block(request):
    try:
        token = get_token(request)
        if token is None:
            return False

        contributor = token.user.contributor
        apiBlock = get_api_block(contributor)
        at_datetime = datetime.datetime.now(tz=timezone.utc)
        return (apiBlock is not None and
                apiBlock.until > at_datetime and apiBlock.active)
    except ObjectDoesNotExist:
        return False
    return False


def token_has_contributor(request):
    try:
        token = get_token(request)
        if token is None:
            return True
        return token.user.contributor is not None
    except ObjectDoesNotExist:
        return False


class RequestMeterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_docs = request.get_full_path() == '/api/docs/?format=openapi'
        is_blocked = has_active_block(request)
        if is_blocked and not is_docs:
            return HttpResponse(json.dumps({'detail': 'API limit exceeded'}),
                                content_type='application/json',
                                status=402)

        if not token_has_contributor(request) and not is_docs:
            return HttpResponse(json.dumps({'detail': 'User has no ' +
                                            'associated contributor'}),
                                content_type='application/json',
                                status=402)

        response = self.get_response(request)
        return response


class OriginSourceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.default_origin_source = getattr(
            settings,
            'INSTANCE_SOURCE',
            'os_hub'
        )

    def __call__(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "SET app.origin_source TO %s",
                [self.default_origin_source]
            )

        response = self.get_response(request)
        return response


class DarkVisitorsMiddleware:

    API_URL = 'https://api.darkvisitors.com/visits'
    TOKEN = getattr(settings, 'DARK_VISITORS_API_KEY', None)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self.TOKEN:
            payload = {
                'request_path': request.path,
                'request_method': request.method,
            }
            headers = {
                'Authorization': f'Bearer {self.TOKEN}',
                'Content-Type': 'application/json',
            }

            threading.Thread(
                target=requests.post,
                args=(self.API_URL,),
                kwargs={'json': payload, 'headers': headers},
                daemon=True,
            ).start()

        return response
