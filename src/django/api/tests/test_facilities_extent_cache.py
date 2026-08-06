"""Tests for facility extent cache key normalization and cache hits."""

from django.http import QueryDict
from django.test import TestCase
from unittest.mock import patch

from api.facilities_extent_cache import FacilitiesExtentCache


class FakeCache:
    """Minimal in-memory cache with Django's get/set interface."""

    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value, timeout=None):
        self.data[key] = value


class FakeCaches:
    """Mimics Django's named cache registry for patching."""

    def __init__(self, cache):
        self.cache = cache

    def __getitem__(self, key):
        return self.cache


class FakeQuerySet:
    """Tracks aggregate calls and returns a fixed extent."""

    def __init__(self, extent):
        self.aggregate_call_count = 0
        self.extent = extent

    def aggregate(self, *args, **kwargs):
        self.aggregate_call_count += 1
        return {'location__extent': self.extent}


class TestFacilitiesExtentCache(TestCase):
    """Verifies extent cache keys reflect only result-changing filters."""

    def test_ignores_non_filter_params(self):
        first = QueryDict(
            'contributors=1&countries=US&page=1&pageSize=50&sort_by=name_asc'
            '&detail=true&number_of_public_contributors=true'
        )
        second = QueryDict(
            'contributors=1&countries=US&page=2&pageSize=25'
            '&sort_by=contributors_desc'
        )
        queryset = FakeQuerySet([1.0, 2.0, 3.0, 4.0])

        with patch(
            'api.facilities_extent_cache.caches',
            FakeCaches(FakeCache()),
        ):
            extent_cache = FacilitiesExtentCache()
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, first),
            )
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, second),
            )

        self.assertEqual(1, queryset.aggregate_call_count)

    def test_sorts_repeated_filter_values(self):
        first = QueryDict('contributors=2&contributors=1&countries=US')
        second = QueryDict('countries=US&contributors=1&contributors=2')
        queryset = FakeQuerySet([1.0, 2.0, 3.0, 4.0])

        with patch(
            'api.facilities_extent_cache.caches',
            FakeCaches(FakeCache()),
        ):
            extent_cache = FacilitiesExtentCache()
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, first),
            )
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, second),
            )

        self.assertEqual(1, queryset.aggregate_call_count)

    def test_includes_filter_params(self):
        first = QueryDict('contributors=1&countries=US')
        second = QueryDict('contributors=1&countries=CA')
        queryset = FakeQuerySet([1.0, 2.0, 3.0, 4.0])

        with patch(
            'api.facilities_extent_cache.caches',
            FakeCaches(FakeCache()),
        ):
            extent_cache = FacilitiesExtentCache()
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, first),
            )
            self.assertEqual(
                queryset.extent,
                extent_cache.get(queryset, second),
            )

        self.assertEqual(2, queryset.aggregate_call_count)

    def test_caches_empty_extent(self):
        query_params = QueryDict('contributors=1')
        queryset = FakeQuerySet(None)

        with patch(
            'api.facilities_extent_cache.caches',
            FakeCaches(FakeCache()),
        ):
            extent_cache = FacilitiesExtentCache()
            self.assertIsNone(extent_cache.get(queryset, query_params))
            self.assertIsNone(extent_cache.get(queryset, query_params))

        self.assertEqual(1, queryset.aggregate_call_count)
