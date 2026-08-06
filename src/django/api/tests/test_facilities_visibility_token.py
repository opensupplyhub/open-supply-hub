"""Tests for facilities response visibility cache tokens."""

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.facilities_visibility_token import facilities_visibility_token


def make_request():
    factory = APIRequestFactory()
    return Request(factory.get('/api/facilities/'))


class TestFacilitiesVisibilityToken(TestCase):
    """Verifies the per-user visibility classes for facilities responses."""

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
