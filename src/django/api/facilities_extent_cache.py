"""Cache helpers for expensive facility search extent calculations."""

import hashlib
import json
from typing import Tuple

from django.conf import settings
from django.contrib.gis.db.models import Extent
from django.core.cache import caches
from django.db import connection, transaction
from django.db.models import QuerySet
from django.http import QueryDict

ExtentTuple = Tuple[float, float, float, float]

# A broad free-text search (~600k rows) overflows the default 4MB work_mem
# while building the TID bitmap for the trigram index, and a lossy bitmap
# rechecks whole heap blocks through immutable_unaccent(), which is slower
# than the sequential scan it replaced. 32MB keeps the bitmap exact at the
# scale of the widest real queries. Transaction-local, so nothing else is
# affected. See OSDEV-3793.
EXTENT_WORK_MEM = '32MB'

FACILITIES_EXTENT_CACHE_KEY_PREFIX = 'facilities_extent'
FACILITIES_EXTENT_CACHE_NON_FILTER_PARAMS = frozenset([
    'detail',
    'format',
    'number_of_public_contributors',
    'page',
    'pageSize',
    'sort_by',
])


class FacilitiesExtentCache:
    """Caches facility search map extents by filter-only query params."""

    def __init__(self):
        self.cache = caches['view_cache']
        self.cache_key_prefix = FACILITIES_EXTENT_CACHE_KEY_PREFIX
        self.cache_non_filter_params = (
            FACILITIES_EXTENT_CACHE_NON_FILTER_PARAMS
        )
        self.cache_timeout = settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS

    def __get_cache_key(self, query_params: QueryDict) -> str:
        canonical_params = [
            [key, sorted(query_params.getlist(key))]
            for key in sorted(query_params)
            if key not in self.cache_non_filter_params
        ]
        params_hash = hashlib.sha256(
            json.dumps(canonical_params, separators=(',', ':')).encode('utf-8')
        ).hexdigest()
        return f'{self.cache_key_prefix}:{params_hash}'

    def get(
        self,
        queryset: QuerySet,
        query_params: QueryDict,
    ) -> ExtentTuple | None:
        """Return the cached extent, computing it on a cache miss."""
        cache_key = self.__get_cache_key(query_params)
        cache_miss = object()
        extent = self.cache.get(cache_key, cache_miss)

        if extent is not cache_miss:
            return extent

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('work_mem', %s, true)",
                    [EXTENT_WORK_MEM],
                )
            extent = (
                queryset.aggregate(Extent('location'))['location__extent']
            )
        self.cache.set(cache_key, extent, self.cache_timeout)
        return extent
