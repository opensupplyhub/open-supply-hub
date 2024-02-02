from api.permissions import referring_host, referring_host_is_allowed

from django.test import TestCase, override_settings


class PermissionsTest(TestCase):
    class MockRequest(object):
        def __init__(self, referer):
            self.META = {}
            if referer is not None:
                self.META["HTTP_REFERER"] = referer

    @override_settings(ALLOWED_HOSTS=[".allowed.org"])
    def test_is_referer_allowed(self):
        def check_host(url):
            return referring_host_is_allowed(
                referring_host(PermissionsTest.MockRequest(url))
            )

        self.assertTrue(check_host("http://allowed.org"))
        self.assertTrue(check_host("http://subdomain.allowed.org"))
        self.assertTrue(check_host("http://allowed.org:6543"))
        self.assertTrue(check_host("http://allowed.org:6543/api/countries"))

        self.assertFalse(check_host("http://notallowed.org"))
        self.assertFalse(check_host("http://allowed.com"))
        self.assertFalse(check_host(""))
        self.assertFalse(check_host(None))
        self.assertFalse(check_host("foo"))
