from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.test import override_settings
from django.urls import reverse


class TilePermissionsTest(APITestCase):
    def setUp(self):
        self.tile_path = reverse(
            "tile",
            kwargs={
                "layer": "facilitygrid",
                "cachekey": "1567700347-1-95f951f7",
                "z": 6,
                "x": 15,
                "y": 29,
                "ext": "pbf",
            },
        )

    @override_settings(ALLOWED_HOSTS=["testserver", ".allowed.org"])
    @override_switch("vector_tile", active=True)
    def test_allowed_hosts_can_fetch_tiles(self):
        response = self.client.get(
            self.tile_path, {}, HTTP_REFERER="http://allowed.org/"
        )
        self.assertEqual(200, response.status_code)

    def test_disallowed_hosts_cannot_fetch_tiles(self):
        response = self.client.get(self.tile_path)
        self.assertEqual(401, response.status_code)
