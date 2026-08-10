from django.core.cache import caches
from django.db.models import Count, F, Func

from api.isic import ISIC4_LEVEL_FIELDS
from api.models.facility.facility_index import FacilityIndex

FACILITY_PROCESSING_CACHE_KEY = 'taxonomy_counts:facility_processing'
FACILITY_PROCESSING_CACHE_TIMEOUT_SECONDS = 3600


def public_facility_index_queryset():
    """Facilities visible on the main search map/list."""
    return FacilityIndex.objects.filter(contributors_count__gt=0)


def _aggregate_array_field_counts(queryset, field_name):
    rows = (
        queryset
        .annotate(value=Func(F(field_name), function='unnest'))
        .values('value')
        .annotate(count=Count('id', distinct=True))
    )
    return [
        row for row in rows
        if row['value'] not in (None, '')
    ]


def compute_facility_processing_counts():
    queryset = public_facility_index_queryset()
    counts = {}

    for field_name in ('facility_type', 'processing_type'):
        for row in _aggregate_array_field_counts(queryset, field_name):
            counts[row['value']] = row['count']

    return counts


def get_facility_processing_counts():
    """
    Return facility/processing type counts cached for one hour.

    Counts change infrequently per category; TTL-only invalidation is
    acceptable for MVP.
    """
    cache = caches['view_cache']
    try:
        cached = cache.get(FACILITY_PROCESSING_CACHE_KEY)
        if cached is not None:
            return cached
    except Exception:
        pass

    counts = compute_facility_processing_counts()

    try:
        cache.set(
            FACILITY_PROCESSING_CACHE_KEY,
            counts,
            FACILITY_PROCESSING_CACHE_TIMEOUT_SECONDS,
        )
    except Exception:
        pass

    return counts


def compute_isic4_counts():
    queryset = public_facility_index_queryset()
    counts = {}

    for level, field_name in ISIC4_LEVEL_FIELDS.items():
        for row in _aggregate_array_field_counts(queryset, field_name):
            counts[f'{level}:{row["value"]}'] = row['count']

    return counts
