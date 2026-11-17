from unittest.mock import patch

from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.test import override_settings
from django.urls import reverse

TILER = 'api.views.tile.get_tile'


@override_settings(ALLOWED_HOSTS=['testserver', '.allowed.org'])
class TileDispatchTest(APITestCase):
    """
    A tile request must run only the query for the layer it asked for.

    get_tile used to select the layer by subscripting a dict literal, and
    Python builds that dict in full before the subscript picks an entry, so
    both tile queries ran and one result was discarded: a grid request also
    built a whole facilities tile for the same bounding box. On production
    the two grid queries were the single largest consumer of the database
    and roughly half that work was thrown away. See OSDEV-3864.

    These assert the query that was not asked for is never called. A test
    that only checked the response would have passed against the old code,
    which is exactly why the bug survived so long.

    There is deliberately no "each known layer builds exactly one tile"
    test. With an if/elif/else that assertion cannot fail, so it would
    document an intention rather than guard it; the real risk is a new
    layer falling through the dispatch, which
    test_an_unknown_layer_builds_nothing covers.
    """

    @staticmethod
    def path(layer):
        return reverse('tile', kwargs={
            'layer': layer,
            'cachekey': '1567700347-1-95f951f7',
            'z': 6, 'x': 15, 'y': 29, 'ext': 'pbf',
        })

    def fetch(self, layer):
        """GET one layer with both tile builders mocked out."""
        with patch(f'{TILER}.get_facilities_vector_tile') as facilities, \
             patch(f'{TILER}.get_facility_grid_vector_tile') as grid:
            facilities.return_value = memoryview(b'facilities-tile')
            grid.return_value = memoryview(b'grid-tile')
            response = self.client.get(
                self.path(layer), {}, HTTP_REFERER='http://allowed.org/'
            )
        return response, facilities, grid

    @override_switch('vector_tile', active=True)
    def test_facilities_layer_does_not_build_the_grid(self):
        response, facilities, grid = self.fetch('facilities')

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, facilities.call_count)
        self.assertEqual(
            0, grid.call_count,
            'a facilities request must not also build a grid tile',
        )

    @override_switch('vector_tile', active=True)
    def test_grid_layer_does_not_build_the_facilities_tile(self):
        response, facilities, grid = self.fetch('facilitygrid')

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, grid.call_count)
        self.assertEqual(
            0, facilities.call_count,
            'a grid request must not also build a facilities tile',
        )

    @override_switch('vector_tile', active=True)
    def test_the_requested_layer_is_the_one_returned(self):
        # The dispatch picks a branch; this pins that it picks the right
        # one, so swapping the arms would fail here rather than silently.
        response, _, _ = self.fetch('facilitygrid')
        self.assertEqual(b'grid-tile', response.content)

    @override_switch('vector_tile', active=True)
    def test_an_unknown_layer_builds_nothing(self):
        # The dict this replaced raised KeyError on an unknown layer. A
        # bare `else` would instead have served a grid tile for it, so
        # this pins that an unrecognised layer still fails rather than
        # silently returning the wrong one.
        with patch(f'{TILER}.get_facilities_vector_tile') as facilities, \
             patch(f'{TILER}.get_facility_grid_vector_tile') as grid:
            response = self.client.get(
                '/tile/notalayer/1567700347-1-95f951f7/6/15/29.pbf',
                {}, HTTP_REFERER='http://allowed.org/',
            )

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(0, facilities.call_count)
        self.assertEqual(0, grid.call_count)
