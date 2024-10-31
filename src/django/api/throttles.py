from django.core.cache import caches
from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import SimpleRateThrottle


class UserCustomRateThrottle(UserRateThrottle):
    """Allow custom per-user throttle rates defined on custom Django user model.

    `model_rate_field`: Specify the throttle rate field. Required.
    """

    cache = caches['api_throttling']

    def allow_request(self, request, view):
        if request.user is not None:
            user_rate = getattr(request.user, self.model_rate_field, self.rate)
            if self.rate != user_rate:
                self.rate = user_rate
                self.num_requests, self.duration = self.parse_rate(self.rate)

        return super(UserCustomRateThrottle, self).allow_request(request, view)


class BurstRateThrottle(UserCustomRateThrottle):
    scope = 'burst'
    model_rate_field = 'burst_rate'


class SustainedRateThrottle(UserCustomRateThrottle):
    scope = 'sustained'
    model_rate_field = 'sustained_rate'


class DataUploadThrottle(UserCustomRateThrottle):
    scope = 'data_upload'
    model_rate_field = 'data_upload_rate'


class TilesThrottle(SimpleRateThrottle):
    scope = 'tiles'
    model_rate_field = 'tiles_rate'

    def allow_request(self, request, view):
        result = super(TilesThrottle, self).allow_request(request, view)
        print(f'allow_request: {result} {self.scope}')
        return result

    def get_cache_key(self, request, view):
        return 'tiles_rate'

    def get_rate(self):
        return '10/minute'
