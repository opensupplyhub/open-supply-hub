"""Tests for compressed view response caching and its cache keys."""

from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from api.view_response_cache import (
    CompressedResponseCache,
    cache_view_response,
)
from api.views.facility.facilities_view_set import (
    facilities_visibility_token,
)


class FakeCache:
    """Minimal in-memory cache with Django's get/set interface."""

    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value, timeout=None):
        self.data[key] = value


class BrokenCache:
    """Cache backend whose operations always raise."""

    def get(self, key, default=None):
        raise RuntimeError('cache down')

    def set(self, key, value, timeout=None):
        raise RuntimeError('cache down')


class FakeCaches:
    """Mimics Django's named cache registry for patching."""

    def __init__(self, cache):
        self.cache = cache

    def __getitem__(self, key):
        return self.cache


def make_request(query_string='', method='get'):
    factory = APIRequestFactory()
    handler = getattr(factory, method)
    path = '/api/facilities/'
    if query_string:
        path = f'{path}?{query_string}'
    return Request(handler(path))


def patched_caches(cache):
    return patch(
        'api.view_response_cache.caches',
        FakeCaches(cache),
    )


class TestCompressedResponseCache(TestCase):
    """Verifies cache key normalization and compressed storage."""

    def test_param_order_does_not_change_key(self):
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')
            first = response_cache.build_key(
                make_request('countries=US&contributors=2&contributors=1')
            )
            second = response_cache.build_key(
                make_request('contributors=1&contributors=2&countries=US')
            )

        self.assertEqual(first, second)

    def test_different_params_produce_different_keys(self):
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')
            keys = {
                response_cache.build_key(make_request(qs))
                for qs in [
                    'countries=US',
                    'countries=CA',
                    'countries=US&page=2',
                    'countries=US&pageSize=10',
                    'countries=US&sort_by=name_asc',
                    'countries=US&detail=true',
                ]
            }

        self.assertEqual(6, len(keys))

    def test_key_prefix_separates_views(self):
        request = make_request('countries=US')
        with patched_caches(FakeCache()):
            first = CompressedResponseCache('one').build_key(request)
            second = CompressedResponseCache('two').build_key(request)

        self.assertNotEqual(first, second)

    def test_view_kwargs_separate_resources(self):
        request = make_request('detail=true')
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')
            first = response_cache.build_key(request, '', {'pk': 'US123'})
            second = response_cache.build_key(request, '', {'pk': 'US999'})
            same = response_cache.build_key(request, '', {'pk': 'US123'})

        self.assertNotEqual(first, second)
        self.assertEqual(first, same)

    def test_vary_token_separates_users(self):
        request = make_request('countries=US')
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')
            anon = response_cache.build_key(request, 'anon:full')
            limited = response_cache.build_key(request, '7:limited')
            default = response_cache.build_key(request)

        self.assertEqual(3, len({anon, limited, default}))

    def test_round_trips_nested_data(self):
        data = {
            'type': 'FeatureCollection',
            'features': [{'id': 'US123', 'properties': {'name': 'A'}}],
            'extent': [1.0, 2.0, 3.0, 4.0],
        }
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')
            response_cache.set('key', data)

            self.assertEqual(data, response_cache.get('key'))

    def test_get_returns_none_on_miss(self):
        with patched_caches(FakeCache()):
            response_cache = CompressedResponseCache('test')

            self.assertIsNone(response_cache.get('missing'))

    @override_settings(VIEW_RESPONSE_CACHE_MAX_BYTES=10)
    def test_oversized_payload_is_not_stored(self):
        fake_cache = FakeCache()
        data = {'features': ['x' * 10000, 'y' * 10000]}
        with patched_caches(fake_cache):
            response_cache = CompressedResponseCache('test')
            response_cache.set('key', data)

            self.assertEqual({}, fake_cache.data)
            self.assertIsNone(response_cache.get('key'))

    def test_broken_cache_fails_open(self):
        with patched_caches(BrokenCache()):
            response_cache = CompressedResponseCache('test')
            response_cache.set('key', {'a': 1})

            self.assertIsNone(response_cache.get('key'))


class FakeView:
    """View double counting how often the wrapped method runs."""

    def __init__(self, status_code=200):
        self.call_count = 0
        self.status_code = status_code

    @cache_view_response('fake_view')
    def list(self, request):
        self.call_count += 1
        return Response(
            {'features': [1, 2, 3]},
            status=self.status_code,
        )

    @cache_view_response('fake_detail')
    def retrieve(self, request, pk=None):
        self.call_count += 1
        return Response({'id': pk}, status=self.status_code)


class TestCacheViewResponseDecorator(TestCase):
    """Verifies the decorator's hit, miss, and bypass behavior."""

    def test_second_identical_request_is_served_from_cache(self):
        view = FakeView()
        with patched_caches(FakeCache()):
            first = view.list(make_request('countries=US'))
            second = view.list(make_request('countries=US'))

        self.assertEqual(1, view.call_count)
        self.assertEqual(first.data, second.data)

    def test_different_requests_are_not_shared(self):
        view = FakeView()
        with patched_caches(FakeCache()):
            view.list(make_request('countries=US'))
            view.list(make_request('countries=CA'))

        self.assertEqual(2, view.call_count)

    def test_non_200_response_is_not_cached(self):
        view = FakeView(status_code=400)
        with patched_caches(FakeCache()):
            view.list(make_request('countries=US'))
            view.list(make_request('countries=US'))

        self.assertEqual(2, view.call_count)

    def test_non_get_request_bypasses_cache(self):
        view = FakeView()
        with patched_caches(FakeCache()):
            view.list(make_request(method='post'))
            view.list(make_request(method='post'))

        self.assertEqual(2, view.call_count)

    def test_detail_requests_are_cached_per_resource(self):
        view = FakeView()
        with patched_caches(FakeCache()):
            first = view.retrieve(make_request(), pk='US123')
            cached = view.retrieve(make_request(), pk='US123')
            other = view.retrieve(make_request(), pk='US999')

        self.assertEqual(2, view.call_count)
        self.assertEqual(first.data, cached.data)
        self.assertEqual({'id': 'US999'}, other.data)


class TestFacilitiesVisibilityToken(TestCase):
    """Verifies the per-user visibility classes for the facilities list."""

    def test_anonymous_user_is_anon_full(self):
        request = make_request()
        request.user = AnonymousUser()

        self.assertEqual('anon:full', facilities_visibility_token(request))

    def test_full_detail_user_includes_contributor_id(self):
        request = make_request()
        request.user = _FakeUser(contributor_id=7, can_view_full=True)

        self.assertEqual('7:full', facilities_visibility_token(request))

    def test_limited_user_is_limited(self):
        request = make_request()
        request.user = _FakeUser(contributor_id=7, can_view_full=False)

        self.assertEqual('7:limited', facilities_visibility_token(request))

    def test_users_with_different_contributors_differ(self):
        first = make_request()
        first.user = _FakeUser(contributor_id=1, can_view_full=True)
        second = make_request()
        second.user = _FakeUser(contributor_id=2, can_view_full=True)

        self.assertNotEqual(
            facilities_visibility_token(first),
            facilities_visibility_token(second),
        )


class _FakeContributor:
    def __init__(self, contributor_id):
        self.id = contributor_id


class _FakeUser:
    is_anonymous = False

    def __init__(self, contributor_id, can_view_full):
        self.contributor = _FakeContributor(contributor_id)
        self.can_view_full_contrib_details = can_view_full
