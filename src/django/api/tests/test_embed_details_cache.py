from api.models import Contributor, EmbedConfig, User
from api.views.facility.facilities_view_set import (
    cache_page_by_auth_tier,
    facilities_cache_token,
    is_embed_request,
)

from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

LOCAL_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'embed-details-cache-test',
    },
}


class EmbedDetailsCacheTest(TestCase):
    """
    What an embedded map is sent for a facility depends on its
    contributor's settings, so a cached copy must not outlive a change to
    them: turning Spotlight off has to take effect at once.
    """

    def setUp(self):
        self.requests = RequestFactory()
        user = User.objects.create(email="brand@example.com")
        self.contributor = Contributor.objects.create(
            admin=user,
            name="Brand",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            embed_level=3,
            embed_config=EmbedConfig.objects.create(),
        )

    def _details_request(self, embed=True):
        url = "/api/facilities/US2020052SV22HT/"
        if embed:
            url += "?embed=1&contributor={}".format(self.contributor.id)
        request = self.requests.get(url)
        request.query_params = request.GET
        return request

    def test_embed_requests_are_recognised(self):
        self.assertTrue(is_embed_request(self._details_request()))
        self.assertFalse(is_embed_request(self._details_request(embed=False)))

    def test_cached_details_vary_by_the_embed_settings(self):
        before = facilities_cache_token(self._details_request())

        config = self.contributor.embed_config
        config.show_spotlight = True
        config.save()

        self.assertNotEqual(
            before, facilities_cache_token(self._details_request())
        )

    def test_details_outside_an_embed_do_not_vary_by_embed_settings(self):
        before = facilities_cache_token(self._details_request(embed=False))

        config = self.contributor.embed_config
        config.show_spotlight = True
        config.save()

        self.assertEqual(
            before, facilities_cache_token(self._details_request(embed=False))
        )

    @override_settings(CACHES=LOCAL_CACHES)
    def test_the_page_cache_is_skipped_for_embed_requests(self):
        calls = []

        class View:
            @cache_page_by_auth_tier(
                60, cache="default", skip_when=is_embed_request
            )
            def retrieve(self, request):
                calls.append(request.get_full_path())
                return HttpResponse("details")

        view = View()
        # Outside an embed the second request is served from the cache.
        view.retrieve(self._details_request(embed=False))
        view.retrieve(self._details_request(embed=False))
        self.assertEqual(1, len(calls))

        # From an embed, every request reaches the view.
        view.retrieve(self._details_request())
        view.retrieve(self._details_request())
        self.assertEqual(3, len(calls))
