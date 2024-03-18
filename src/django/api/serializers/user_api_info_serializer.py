from django.utils import timezone
from api.models import (RequestLog, ApiLimit)
from api.limitation.date.monthly_date_limitation import MonthlyDateLimitation
from api.limitation.date.yearly_date_limitation import YearlyDateLimitation
from django.core.exceptions import ObjectDoesNotExist


class UserApiInfoSerializer:
    data: dict

    def __init__(self, uid, contributor_id):
        self.data = {
            "api_call_limit": self.__get_api_call_limit(contributor_id),
            "renewal_period": self.__get_renewal_period(contributor_id),
            "current_usage": self.__get_current_usage(uid, contributor_id),
        }

    def __get_start_end_date_for_current_usage(self, contributor_id):
        try:
            apiLimit = ApiLimit.objects.get(
                contributor_id=contributor_id)
            renewal_period = apiLimit.renewal_period
            date = apiLimit.period_start_date
        except ObjectDoesNotExist:
            apiLimit = None
            renewal_period = ''

        if renewal_period == '':
            return {}
        if renewal_period == 'MONTHLY':
            date_limitation = MonthlyDateLimitation()
        if renewal_period == 'YEARLY':
            date_limitation = YearlyDateLimitation()

        date_limitation.execute(date)

        return {
                "start_date": date_limitation.get_start_date(),
                "end_date": timezone.now()
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

    def __get_current_usage(self, uid, contributor_id):
        range_of_dates = self.__get_start_end_date_for_current_usage(
            contributor_id)

        if not range_of_dates:
            return 0

        try:
            successful_calls = RequestLog.objects.filter(
                response_code__gte=200,
                response_code__lte=299,
                created_at__gte=range_of_dates["start_date"],
                created_at__lte=range_of_dates["end_date"],
                user_id=uid).count()
            return successful_calls
        except RequestLog.DoesNotExist:
            return 0
