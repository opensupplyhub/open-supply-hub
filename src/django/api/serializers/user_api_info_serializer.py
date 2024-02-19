
from rest_framework.exceptions import ValidationError
from api.models import (RequestLog, ApiLimit)
from api.models.contributor.contributor import Contributor


class UserApiInfoSerializer:
    uid: int
    contributor_id: int

    def __init__(self, uid):
        self.uid = uid

        try:
            contributor = Contributor.objects.get(admin_id=self.uid)
            self.contributor_id = contributor.id
        except Contributor.DoesNotExist:
            raise ValidationError((
                    f"User with id = {self.uid} doesn't has a contributor"
            ))

    def get_api_call_limit(self):
        try:
            period_limit = ApiLimit.objects.get(
                contributor_id=self.contributor_id).period_limit
            return str(period_limit)
        except ApiLimit.DoesNotExist:
            return '403 Forbidden'

    def get_renewal_period(self):
        try:
            renewal_period = ApiLimit.objects.get(
                contributor_id=self.contributor_id).renewal_period
            if renewal_period == '':
                return 'Is not set'
            else:
                return renewal_period
        except ApiLimit.DoesNotExist:
            return 'Is not set'

    def get_current_usage(self):
        try:
            successful_calls = RequestLog.objects.filter(
                response_code__gte=200,
                response_code__lte=299,
                user_id=self.uid).count()
            return str(successful_calls)
        except RequestLog.DoesNotExist:
            return 0
