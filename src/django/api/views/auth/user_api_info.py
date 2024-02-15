from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import (RequestLog, ApiLimit)
from ...models import Contributor


def get_api_call_limit(contributor_id):
    try:
        period_limit = ApiLimit.objects.get(
            contributor_id=contributor_id).period_limit
        return str(period_limit)
    except ApiLimit.DoesNotExist:
        return '403 Forbidden'


def get_renewal_period(contributor_id):
    try:
        renewal_period = ApiLimit.objects.get(
            contributor_id=contributor_id).renewal_period
        return renewal_period
    except ApiLimit.DoesNotExist:
        return 'Is not set'


def get_current_usage(u_id):
    try:
        successful_calls = RequestLog.objects.filter(
            response_code__gte=200,
            response_code__lte=299,
            user_id=u_id).count()
        return str(successful_calls)
    except RequestLog.DoesNotExist:
        return -1


class UserAPIInfo(APIView):
    def get(self, request, uid=None, *args, **kwaurlsrgs):
        print("!!!! uid", uid)
        try:
            contributor = Contributor.objects.get(admin_id=uid)
        except Contributor.DoesNotExist:
            print("!!!! contributor", contributor)

        period_limit = get_api_call_limit(contributor.id)
        renewal_period = get_renewal_period(contributor.id)
        successful_calls = get_current_usage(uid)
        api_call_info_data = {
            "apiCallAllowance": period_limit,
            "currentCallCount": successful_calls,
            "renewalPeriod": renewal_period,
        }
        print("!!!! api_call_info_data", api_call_info_data)

        return Response(api_call_info_data)
