"""Generic compressed response caching for DRF view methods.

Memcached rejects items over its per-item size limit (~5 MB), which makes
plain ``cache_page`` unusable for endpoints with large, variable payloads.
This module compresses response data before caching and skips the cache
write entirely when the compressed payload is still too large, so a
response is either cached safely or served uncached (fail-open).
"""

import hashlib
import json
import zlib
from functools import wraps
from typing import Any, Callable, Optional

from django.conf import settings
from django.core.cache import caches
from django.http import HttpRequest
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class CompressedResponseCache:
    """Stores JSON-serializable response data compressed in memcached.

    Cache keys are built from a canonical form of the request query params
    (sorted keys, sorted multi-values) plus an optional vary token, so
    logically identical requests share an entry regardless of param order.
    All cache errors are swallowed: a failing cache never breaks a request.
    """

    def __init__(self, key_prefix: str):
        self.cache = caches['view_cache']
        self.key_prefix = key_prefix
        self.timeout = settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS
        self.max_bytes = settings.VIEW_RESPONSE_CACHE_MAX_BYTES

    def build_key(
        self,
        request: HttpRequest,
        vary_token: str = '',
        view_kwargs: Optional[dict] = None,
    ) -> str:
        """Return a cache key for the request's query params, URL kwargs,
        and vary token.

        URL kwargs (e.g. ``pk``) are included so detail endpoints keyed on
        a path variable do not collide across resources.
        """
        query_params = request.query_params
        canonical_params = [
            [key, sorted(query_params.getlist(key))]
            for key in sorted(query_params)
        ]
        canonical_kwargs = sorted(
            (str(key), str(value))
            for key, value in (view_kwargs or {}).items()
        )
        payload = json.dumps(
            [canonical_params, canonical_kwargs, vary_token],
            separators=(',', ':'),
        )
        params_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        return f'{self.key_prefix}:{params_hash}'

    def get(self, key: str) -> Optional[Any]:
        """Return the cached data or None on a miss or any cache error."""
        try:
            compressed = self.cache.get(key)
            if compressed is None:
                return None
            return json.loads(zlib.decompress(compressed))
        except Exception:
            return None

    def set(self, key: str, data: Any) -> None:
        """Compress and store data, skipping payloads over the size limit.

        Data is serialized with DRF's JSONRenderer so types the standard
        json encoder rejects (Decimal, datetime, lazy strings) are handled
        the same way as in the actual HTTP response.
        """
        try:
            compressed = zlib.compress(JSONRenderer().render(data))
            if len(compressed) <= self.max_bytes:
                self.cache.set(key, compressed, self.timeout)
        except Exception:
            pass


def cache_view_response(
    key_prefix: str,
    vary_on: Optional[Callable[[HttpRequest], str]] = None,
) -> Callable:
    """Cache a DRF view method's response data, compressed, in memcached.

    Works on any DRF class-based view or viewset method. Only GET requests
    are cached, and only responses with a 200 status. URL kwargs (e.g.
    ``pk``) are part of the cache key, so detail endpoints keyed on a path
    variable are cached per resource.

    Arguments:
    key_prefix (str) -- Namespace for this view's cache entries.
    vary_on (callable) -- Optional callable taking the request and
        returning a string appended to the cache key. Use it when the
        response content varies per user (e.g. visibility rules).
    """
    def decorator(view_method):
        @wraps(view_method)
        def _wrapped(self, request, *args, **kwargs):
            if request.method != 'GET':
                return view_method(self, request, *args, **kwargs)

            response_cache = CompressedResponseCache(key_prefix)
            vary_token = vary_on(request) if vary_on else ''
            cache_key = response_cache.build_key(
                request, vary_token, kwargs
            )

            cached_data = response_cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            response = view_method(self, request, *args, **kwargs)
            if response.status_code == 200:
                response_cache.set(cache_key, response.data)
            return response
        return _wrapped
    return decorator
