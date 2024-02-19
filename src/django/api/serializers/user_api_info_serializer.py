from api.models import (RequestLog, ApiLimit)


class UserApiInfoSerializer:
    data: dict

    def __init__(self, uid, contributor_id):
        self.data = {
            "api_call_limit": self.__get_api_call_limit(contributor_id),
            "current_usage": self.__get_current_usage(uid),
            "renewal_period": self.__get_renewal_period(contributor_id),
        }

    def __get_api_call_limit(self, contributor_id):
        try:
            period_limit = ApiLimit.objects.get(
                contributor_id=contributor_id).period_limit
            return str(period_limit)
        except ApiLimit.DoesNotExist:
            return 'Is not set'

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
            return successful_calls
        except RequestLog.DoesNotExist:
            return 0
