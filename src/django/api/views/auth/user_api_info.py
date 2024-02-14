# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_auth.views import LoginView
# from api.limits import check_contributor_api_limit
# from django.utils import timezone
from api.models import (RequestLog, ApiLimit)
from ...models import Contributor


def get_api_call_limit(contributor_id):
    try:
        period_limit = ApiLimit.objects.get(
            contributor_id=contributor_id).period_limit
        return period_limit
    except ApiLimit.DoesNotExist:
        return -1


def get_renewal_period(contributor_id):
    try:
        renewal_period = ApiLimit.objects.get(
            contributor_id=contributor_id).renewal_period
        return renewal_period
    except ApiLimit.DoesNotExist:
        return -1


def get_current_usage(u_id):
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

        period_limit = get_api_call_limit(contributor.id)
        renewal_period = get_renewal_period(contributor.id)
        successful_calls = get_current_usage(pk)
        api_call_info_data = {
            "apiCallAllowance": period_limit,
            "currentCallCount": successful_calls,
            "renewalPeriod": renewal_period,
        }

        return Response(api_call_info_data)
