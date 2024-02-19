
from rest_framework.exceptions import ValidationError
from api.models import (RequestLog, ApiLimit)
from api.models.contributor.contributor import Contributor


class UserApiInfoSerializer:
    data: dict

    def __init__(self, uid):

        try:
            contributor = Contributor.objects.get(admin_id=uid)
            contributor_id = contributor.id
        except Contributor.DoesNotExist:
            raise ValidationError((
                    f"User with id = {uid} doesn't has a contributor"
            ))

        self.data = {
            "apiCallAllowance": self.__get_api_call_limit(contributor_id),
            "currentCallCount": self.__get_current_usage(uid),
            "renewalPeriod": self.__get_renewal_period(contributor_id),
        }

    def __get_api_call_limit(self, contributor_id):
        try:
            period_limit = ApiLimit.objects.get(
                contributor_id=contributor_id).period_limit
            return str(period_limit)
        except ApiLimit.DoesNotExist:
            return '403 Forbidden'

    def __get_renewal_period(self, contributor_id):
        try:
            renewal_period = ApiLimit.objects.get(
                contributor_id=contributor_id).renewal_period
            if renewal_period == '':
                return 'Is not set'
            else:
                return renewal_period
        except ApiLimit.DoesNotExist:
            return 'Is not set'

    def __get_current_usage(self, uid):
        try:
            successful_calls = RequestLog.objects.filter(
                response_code__gte=200,
                response_code__lte=299,
                user_id=uid).count()
            return str(successful_calls)
        except RequestLog.DoesNotExist:
            return 0
