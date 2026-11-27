from django.conf import settings
from django.core.cache import caches
from django.test import SimpleTestCase

from waffle.utils import get_cache, get_setting


class WaffleCacheSettingsTest(SimpleTestCase):
    """Waffle must read switch state from a cross-process cache so a
    toggle made in admin reaches every Django process (OSDEV-3742)."""

    def test_waffle_uses_its_own_named_cache(self):
        self.assertEqual(get_setting('CACHE_NAME'), 'waffle')
        self.assertIn('waffle', settings.CACHES)
        self.assertIs(get_cache(), caches['waffle'])

    def test_waffle_max_age_is_bounded(self):
        max_age = get_setting('MAX_AGE')
        self.assertGreater(max_age, 0)
        self.assertLessEqual(max_age, 300)
