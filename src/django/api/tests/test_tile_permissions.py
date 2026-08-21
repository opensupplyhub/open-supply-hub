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

    @override_settings(ALLOWED_HOSTS=["testserver", ".allowed.org"])
    @override_switch("vector_tile", active=True)
    def test_facility_grid_supports_free_text_processing_and_isic_filters(
        self,
    ):
        response = self.client.get(
            self.tile_path,
            {
                "processing_type": "x[yz",
                "isic_4": "section:C",
                "combine_facility_processing_isic": "AND",
                "sort_by": "contributors_desc",
            },
            HTTP_REFERER="http://allowed.org/",
        )

        self.assertEqual(200, response.status_code)

    @override_settings(ALLOWED_HOSTS=["testserver", ".allowed.org"])
    @override_switch("vector_tile", active=True)
    def test_both_tile_layers_support_exact_processing_type_filter(self):
        for layer in ("facilities", "facilitygrid"):
            with self.subTest(layer=layer):
                tile_path = reverse(
                    "tile",
                    kwargs={
                        "layer": layer,
                        "cachekey": "1567700347-1-95f951f7",
                        "z": 6,
                        "x": 15,
                        "y": 29,
                        "ext": "pbf",
                    },
                )
                response = self.client.get(
                    tile_path,
                    {
                        "processing_type": "CAPS",
                        "processing_type_exact": "CAPS",
                    },
                    HTTP_REFERER="http://allowed.org/",
                )

                self.assertEqual(200, response.status_code)

    def test_disallowed_hosts_cannot_fetch_tiles(self):
        response = self.client.get(self.tile_path)
        self.assertEqual(401, response.status_code)
