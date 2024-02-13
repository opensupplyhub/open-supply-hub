# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_auth.views import LoginView
# from api.limits import check_contributor_api_limit
# from django.utils import timezone
from api.models import (RequestLog, ApiLimit)
from ...models import Contributor


def getApiCallLimit(contributor_id):
    try:
        limit = ApiLimit.objects.get(
            contributor_id=contributor_id).yearly_limit
        return limit
    except ApiLimit.DoesNotExist:
        return -1


def getCurrentUsage(u_id):
    try:
        successful_calls = RequestLog.objects.filter(
            response_code__gte=200,
            response_code__lte=299,
            user_id=u_id).count()
        return successful_calls
    except RequestLog.DoesNotExist:
        return -1


class UserApiInfo(LoginView):
    def get(self, request, pk):
        try:
            contributor = Contributor.objects.get(admin_id=pk)
        except Contributor.DoesNotExist:
            print("!!!! contributor", contributor)
        # u_id = 222
        # contributor_id = 221
        # check_contributor_api_limit(timezone.now(), contributor_id)
# via annotate get contributor!!!! limits.py
        # print("!!!! contributor_logs", successful_calls, apiLimit, limit,)
        api_call_info_data = {
            "apiCallAllowance": '5000',  # limit
            "currentCallCount": '4200',  # successful_calls
            "renewalPeriod": 'Monthly',  # todo
        }

        return Response(api_call_info_data)
