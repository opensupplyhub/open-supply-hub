from django.test import RequestFactory, TestCase

from api.throttles import BurstRateThrottle, SustainedRateThrottle
from api.views.v1.identity_resolver import (
    IdentityResolverView,
    ResolverDescriptionView,
)


class IdentityResolverThrottlingTest(TestCase):
    """
    The resolver is public and unauthenticated, so throttling is the only
    thing standing between it and abuse (OSDEV-3587).

    These assert inheritance rather than exercising the limit. Issuing a
    hundred requests would test DRF, which is already tested; what can
    actually regress here is someone adding `throttle_classes = []` to the
    view, or an authentication class that changes how callers are
    identified. Both of those break silently and neither shows up anywhere
    else.
    """

    def test_resolver_inherits_the_project_throttles(self):
        throttles = IdentityResolverView().get_throttles()
        classes = {type(t) for t in throttles}

        self.assertIn(BurstRateThrottle, classes)
        self.assertIn(SustainedRateThrottle, classes)

    def test_resolver_description_inherits_them_too(self):
        throttles = ResolverDescriptionView().get_throttles()
        classes = {type(t) for t in throttles}

        self.assertIn(BurstRateThrottle, classes)
        self.assertIn(SustainedRateThrottle, classes)

    def test_anonymous_callers_are_counted_per_client_address(self):
        """
        DRF's user throttle falls back to the client address when there is
        no authenticated user. The resolver sets `authentication_classes`
        to empty, so every caller takes that path and the limit is per
        address rather than shared across everyone at once.
        """
        request = RequestFactory().get(
            '/osid/XX2000001AAAAA5', REMOTE_ADDR='198.51.100.7'
        )
        request.user = None

        key = BurstRateThrottle().get_cache_key(request, None)

        self.assertIn('198.51.100.7', key)

    def test_two_addresses_do_not_share_an_allowance(self):
        factory = RequestFactory()
        throttle = BurstRateThrottle()

        first = factory.get('/osid/X', REMOTE_ADDR='198.51.100.7')
        second = factory.get('/osid/X', REMOTE_ADDR='203.0.113.9')
        first.user = None
        second.user = None

        self.assertNotEqual(
            throttle.get_cache_key(first, None),
            throttle.get_cache_key(second, None),
        )
