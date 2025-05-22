import hashlib
import json
from django.utils import timezone
from django.core.cache import caches
from rest_framework.throttling import (
    UserRateThrottle,
    BaseThrottle
)
from rest_framework.exceptions import Throttled
from oar.settings import DUPLICATE_THROTTLE_TIMEOUT


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


class DuplicateThrottle(BaseThrottle):
    cache = caches['api_throttling']
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB limit

    def _serialize_data(self, data):
        try:
            return json.dumps(data, sort_keys=True)
        except (TypeError, ValueError):
            return str(data)

    def allow_request(self, request, view):
        if request.method not in ["POST", "PATCH"]:
            return True

        if not request.user.is_authenticated:
            return False

        if not request.data:
            return True

        data_str = self._serialize_data(request.data)
        if len(data_str.encode()) > self.MAX_REQUEST_SIZE:
            raise Throttled(
                detail="Request data too large. Maximum size is 1MB."
            )

        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        cache_key = f"duplicate:{request.user.id}:{data_hash}"

        if self.cache.get(cache_key):
            raise Throttled(
                detail="Duplicate request submitted, please try again later."
            )

        self.cache.set(
            cache_key,
            timezone.now(),
            timeout=DUPLICATE_THROTTLE_TIMEOUT
        )
        return True
