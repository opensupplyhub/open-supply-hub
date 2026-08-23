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
    """Allow per-user throttle rates defined on the custom user model.

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

    # Query params that change a request's effective behavior and so should
    # produce a distinct cache key. Only their "true" state is recognized -
    # see _canonical_overrides.
    OVERRIDE_QUERY_PARAMS = ("duplicate_override", "ignore_warnings")

    def _serialize_data(self, data):
        try:
            return json.dumps(data, sort_keys=True)
        except (TypeError, ValueError):
            return str(data)

    def _canonical_overrides(self, request):
        # Only a recognized override flag in its "true" state changes a
        # request's effective behavior; an absent flag, an explicit
        # "=false", or any unrelated query param is equivalent to the
        # default. Hashing only the true-valued flags keeps an override
        # retry (e.g. ?duplicate_override=true) distinct from the original,
        # while stopping a semantically-identical request that merely adds
        # ?ignore_warnings=false (or any other param) from getting a fresh
        # cache key and bypassing the throttle.
        return sorted(
            name for name in self.OVERRIDE_QUERY_PARAMS
            if request.query_params.get(name) == "true"
        )

    def _build_cache_key(self, request, view):
        data_str = self._serialize_data(request.data)
        pk = view.kwargs.get("pk")
        pk_prefix = f":{pk}" if pk else ""
        query_str = self._serialize_data(self._canonical_overrides(request))
        data_hash = hashlib.sha256(
            f"{data_str}{query_str}".encode()
        ).hexdigest()
        return f"duplicate:{request.user.id}{pk_prefix}:{data_hash}"

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

        cache_key = self._build_cache_key(request, view)

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

    def clear(self, request, view):
        """
        Remove the throttle entry recorded for this request. Views call this
        when a request is rejected without side effects (e.g. a 409 from the
        duplicate or submission-quality check), so an identical retry isn't
        blocked as a duplicate of an attempt that created nothing. The entry
        is still recorded up front by allow_request, which keeps concurrent
        identical requests (double-clicks) blocked while the first one is
        in flight.
        """
        if request.method not in ["POST", "PATCH"]:
            return
        if not request.user.is_authenticated or not request.data:
            return
        self.cache.delete(self._build_cache_key(request, view))
