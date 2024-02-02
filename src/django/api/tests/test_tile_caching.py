import time

from api.models import DynamicSetting
from api.views.tile.utils import retrieve_cached_tile
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.db import connection
from django.test import override_settings
from django.urls import reverse


class TileCachingTest(APITestCase):
    def setUp(self):
        self.domain = "http://allowed.org/"
        self.tile_path = reverse(
            "tile",
            kwargs={
                "layer": "facilitygrid",
                "cachekey": "1567700347-1-95f951f7",
                "z": 6,
                "x": 20,
                "y": 21,
                "ext": "pbf",
            },
        )

    @override_settings(ALLOWED_HOSTS=["testserver", ".allowed.org"])
    @override_switch("vector_tile", active=True)
    def make_tile_request(self):
        response = self.client.get(
            self.tile_path, {}, HTTP_REFERER=self.domain
        )
        return response.status_code

    def test_a_requested_tile_is_cached(self):
        self.assertEqual(200, self.make_tile_request())

        cached_tile, created = retrieve_cached_tile(self.tile_path)
        self.assertEqual(0, cached_tile.counter)
        self.assertFalse(created)

    def test_requested_cached_tile_is_returned_from_cache(self):
        self.assertEqual(200, self.make_tile_request())
        self.assertEqual(200, self.make_tile_request())

        cached_tile, created = retrieve_cached_tile(self.tile_path)
        self.assertEqual(1, cached_tile.counter)
        self.assertFalse(created)

    def test_expiration_time_of_cached_tile(self):
        dynamic_settings = DynamicSetting.load()
        dynamic_settings.cached_tile_expiration_time = 20
        dynamic_settings.save()

        self.assertEqual(200, self.make_tile_request())
        cached_tile1, created1 = retrieve_cached_tile(self.tile_path)
        self.assertEqual(0, cached_tile1.counter)
        self.assertFalse(created1)

        self.assertEqual(200, self.make_tile_request())
        cached_tile2, created2 = retrieve_cached_tile(self.tile_path)
        self.assertEqual(cached_tile1.value, cached_tile2.value)
        self.assertEqual(1, cached_tile2.counter)
        self.assertFalse(created2)

        # Force deletion of the temporary hex_grid table since the test is run
        # in one DB transaction and the hex_grid table will not be deleted by
        # the logic of CREATE TEMP TABLE because the DB transaction is not
        # completed.
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS hex_grid")

        time.sleep(25)

        # Verify that the cached tile binary data and the associated URL path
        # have expired, and consequently, the entry with the previously
        # stored path was refreshed with new tile binary data and the counter
        # field was reset to zero.
        self.assertEqual(200, self.make_tile_request())
        cached_tile3, created3 = retrieve_cached_tile(self.tile_path)
        self.assertEqual(cached_tile2.value, cached_tile3.value)
        self.assertEqual(0, cached_tile3.counter)
        self.assertEqual(cached_tile1.created_at, cached_tile3.created_at)
        self.assertFalse(created3)
