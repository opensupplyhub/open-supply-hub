from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase

from api.helpers.geojson_polygon import InvalidPolygonGeoJSON
from api.helpers.zone_subdivision import (
    ZONE_PIECE_MAX_VERTICES,
    subdivide_zone_records,
)
from api.migrations._migration_helper import MigrationHelper
from api.models import Zone, ZoneSet
from api.tests.zone_fixtures import DISC, feature, records

SQUARE = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]
EAST_SQUARE = [[[10, 0], [10, 10], [20, 10], [20, 0], [10, 0]]]

# The budget 0272_subdivide_zones.sql has written into it: the value of
# ZONE_PIECE_MAX_VERTICES when the migration was written. The migration
# is frozen, so this stays 64 even if the constant moves.
MIGRATION_BUDGET = 64


def pieces(*features):
    """The storage pieces for the features, as replace_zones takes them."""
    return subdivide_zone_records(records(*features))


def grid_points(xmin, ymin, xmax, ymax, step):
    """Sample points over a box, including points on its edges."""
    points = []
    x = xmin
    while x <= xmax + 1e-9:
        y = ymin
        while y <= ymax + 1e-9:
            points.append(Point(x, y, srid=4326))
            y += step
        x += step
    return points


class SubdivideZoneRecordsTest(TestCase):
    """Tests for cutting parsed zone records into pieces."""

    def test_large_feature_becomes_pieces_within_the_budget(self):
        [record] = records(feature(DISC, {'bws_label': 'High', 'k': 1}))

        pieces = subdivide_zone_records([record])

        self.assertGreater(len(pieces), 1)
        self.assertEqual(
            [piece['piece_index'] for piece in pieces],
            list(range(len(pieces))),
        )
        for piece in pieces:
            self.assertEqual(piece['feature_index'], 0)
            self.assertEqual(piece['label'], 'High')
            self.assertEqual(
                piece['properties'], {'bws_label': 'High', 'k': 1}
            )
            self.assertEqual(piece['geom'].geom_type, 'MultiPolygon')
            self.assertEqual(piece['geom'].srid, 4326)
            self.assertLessEqual(
                piece['geom'].num_coords, ZONE_PIECE_MAX_VERTICES
            )
            self.assertTrue(piece['geom'].valid)

    def test_pieces_cover_exactly_the_source_feature(self):
        """The pieces partition the feature: their union has the same
        area, and every sample point inside or outside the source is
        inside or outside the union."""
        [record] = records(feature(DISC, {'bws_label': 'High'}))

        pieces = subdivide_zone_records([record])

        union = pieces[0]['geom']
        for piece in pieces[1:]:
            union = union.union(piece['geom'])
        self.assertAlmostEqual(union.area, record['geom'].area, places=9)
        for point in grid_points(25, 25, 75, 75, 2.5):
            self.assertEqual(
                union.covers(point), record['geom'].covers(point), point.wkt
            )

    def test_small_feature_is_a_single_unchanged_piece(self):
        [record] = records(feature(SQUARE, {'bws_label': 'Low'}))

        pieces = subdivide_zone_records([record])

        self.assertEqual(len(pieces), 1)
        self.assertEqual(pieces[0]['feature_index'], 0)
        self.assertEqual(pieces[0]['piece_index'], 0)
        self.assertTrue(pieces[0]['geom'].equals_exact(record['geom'], 0))

    def test_pieces_keep_file_order_across_features(self):
        pieces = subdivide_zone_records(records(
            feature(DISC, {'bws_label': 'High'}),
            feature(SQUARE, {'bws_label': 'Low'}),
            feature(EAST_SQUARE, {'bws_label': 'Medium'}),
        ))

        feature_indexes = [piece['feature_index'] for piece in pieces]
        self.assertEqual(feature_indexes, sorted(feature_indexes))
        self.assertEqual(feature_indexes[-2:], [1, 2])
        self.assertEqual(pieces[-2]['label'], 'Low')
        self.assertEqual(pieces[-1]['label'], 'Medium')

    def test_budget_is_respected(self):
        [record] = records(feature(DISC, {'bws_label': 'High'}))

        coarse = subdivide_zone_records([record], max_vertices=256)
        fine = subdivide_zone_records([record], max_vertices=16)

        self.assertLess(len(coarse), len(fine))
        self.assertTrue(all(p['geom'].num_coords <= 16 for p in fine))

    def test_feature_with_no_pieces_is_refused(self):
        """A feature PostGIS returns no piece for raises instead of
        silently disappearing from the set."""
        record = records(feature(SQUARE, {'bws_label': 'Low'}))[0]
        cursor = Mock()
        cursor.fetchall.return_value = []
        connection_mock = Mock()
        connection_mock.cursor.return_value.__enter__ = Mock(
            return_value=cursor
        )
        connection_mock.cursor.return_value.__exit__ = Mock(
            return_value=False
        )
        with patch(
            'api.helpers.zone_subdivision.connection', connection_mock
        ):
            with self.assertRaisesRegex(
                InvalidPolygonGeoJSON, r'position\(s\) \[0\]'
            ):
                subdivide_zone_records([record])

    def test_empty_input(self):
        self.assertEqual(subdivide_zone_records([]), [])


class ReplaceZonesSubdividesTest(TestCase):
    """Tests for how a zone set stores and resolves subdivided zones."""

    def setUp(self):
        self.zone_set = ZoneSet.objects.create(
            name='aqueduct_bws',
            description='Baseline water stress bands.',
            value_property='bws_label',
        )

    def test_pieces_are_stored_with_the_feature_value(self):
        self.zone_set.replace_zones(pieces(
            feature(DISC, {'bws_label': 'High', 'bws_cat': 3}),
        ))

        zones = list(self.zone_set.zones.all())
        self.assertGreater(len(zones), 1)
        self.assertEqual(
            [(zone.feature_index, zone.piece_index) for zone in zones],
            [(0, index) for index in range(len(zones))],
        )
        for zone in zones:
            self.assertEqual(zone.label, 'High')
            self.assertEqual(
                zone.value['properties'], {'bws_label': 'High', 'bws_cat': 3}
            )
            self.assertLessEqual(zone.geom.num_coords, ZONE_PIECE_MAX_VERTICES)

    def test_resolve_zone_returns_the_same_label_as_the_undivided_feature(
        self,
    ):
        """Every sample point, including ones on the pieces' cut lines,
        resolves to the label the whole feature would have given it,
        and points outside resolve to nothing (AC #1)."""
        [record] = records(feature(DISC, {'bws_label': 'High'}))
        self.zone_set.replace_zones(subdivide_zone_records([record]))
        # Points on cut lines: the pieces' bounding-box edges are the
        # cut lines, so probe the middle of each piece's extent edges.
        on_cuts = []
        for zone in self.zone_set.zones.all():
            xmin, ymin, xmax, ymax = zone.geom.extent
            on_cuts.extend([
                Point(xmin, (ymin + ymax) / 2, srid=4326),
                Point((xmin + xmax) / 2, ymax, srid=4326),
            ])

        for point in grid_points(25, 25, 75, 75, 2.5) + on_cuts:
            resolved = self.zone_set.resolve_zone(point)
            if record['geom'].covers(point):
                self.assertIsNotNone(resolved, point.wkt)
                self.assertEqual(resolved.label, 'High', point.wkt)
            else:
                self.assertIsNone(resolved, point.wkt)

    def test_earlier_feature_still_wins_on_a_shared_edge_and_overlap(self):
        """Precedence follows the source feature's position in the
        file, not the piece order (AC #3)."""
        # A big disc first, then a square overlapping it, then a square
        # touching the disc's bounding region only along x = 70.
        self.zone_set.replace_zones(pieces(
            feature(DISC, {'bws_label': 'High'}),
            feature([[[60, 40], [60, 60], [80, 60], [80, 40], [60, 40]]],
                    {'bws_label': 'Low'}),
        ))
        # Inside both: the disc (feature 0) wins, although some of its
        # pieces have higher ids than the square.
        self.assertEqual(
            self.zone_set.resolve_zone(Point(65, 50, srid=4326)).label, 'High'
        )
        # Inside the square only.
        self.assertEqual(
            self.zone_set.resolve_zone(Point(75, 45, srid=4326)).label, 'Low'
        )
        # Reverse the file order: the square wins the overlap.
        self.zone_set.replace_zones(pieces(
            feature([[[60, 40], [60, 60], [80, 60], [80, 40], [60, 40]]],
                    {'bws_label': 'Low'}),
            feature(DISC, {'bws_label': 'High'}),
        ))
        self.assertEqual(
            self.zone_set.resolve_zone(Point(65, 50, srid=4326)).label, 'Low'
        )

    def test_shared_edge_between_two_features(self):
        self.zone_set.replace_zones(pieces(
            feature(EAST_SQUARE, {'bws_label': 'Low'}),
            feature(SQUARE, {'bws_label': 'High'}),
        ))
        self.assertEqual(
            self.zone_set.resolve_zone(Point(10, 5, srid=4326)).label, 'Low'
        )

    def test_reupload_replaces_every_piece(self):
        self.zone_set.replace_zones(pieces(
            feature(DISC, {'bws_label': 'High'}),
        ))
        old_ids = set(self.zone_set.zones.values_list('id', flat=True))

        self.zone_set.replace_zones(pieces(
            feature(SQUARE, {'bws_label': 'Low'}),
        ))

        self.assertFalse(Zone.objects.filter(id__in=old_ids).exists())
        self.assertEqual(self.zone_set.zones.count(), 1)

    def test_str_names_feature_and_piece(self):
        self.zone_set.replace_zones(pieces(
            feature(SQUARE, {'bws_label': 'Low'}),
        ))
        self.assertEqual(
            str(self.zone_set.zones.get()), 'aqueduct_bws #0.0: Low'
        )


class SubdivideExistingZonesMigrationTest(TestCase):
    """Tests for the 0272 data step that re-cuts zones saved before
    subdivision existed, and its reverse."""

    def setUp(self):
        self.zone_set = ZoneSet.objects.create(
            name='legacy_bws',
            description='Uploaded before subdivision.',
            value_property='bws_label',
        )
        # One row per feature, as replace_zones used to write them.
        for index, record in enumerate(records(
            feature(DISC, {'bws_label': 'High'}),
            feature(SQUARE, {'bws_label': 'Low'}),
        )):
            Zone.objects.create(
                zone_set=self.zone_set,
                feature_index=index,
                geom=record['geom'],
                value={'label': record['label'], 'properties': {}},
            )
        self.helper = MigrationHelper(connection)

    def _labels_on_grid(self):
        """The resolved label (or None) for each point of a grid over
        both features."""
        return {
            point.wkt: getattr(
                self.zone_set.resolve_zone(point), 'label', None
            )
            for point in grid_points(0, 0, 80, 80, 4)
        }

    def test_forward_cuts_rows_in_place_and_keeps_coverage(self):
        """Pieces appear with their feature's value and index, the
        small feature stays one row, and labels resolve as before."""
        before = self._labels_on_grid()
        legacy_created_at = self.zone_set.zones.get(feature_index=0).created_at

        self.helper.run_sql_file('0272_subdivide_zones.sql')

        disc_pieces = self.zone_set.zones.filter(feature_index=0)
        self.assertGreater(disc_pieces.count(), 1)
        self.assertEqual(
            list(disc_pieces.values_list('piece_index', flat=True)),
            list(range(disc_pieces.count())),
        )
        for piece in disc_pieces:
            self.assertEqual(piece.label, 'High')
            self.assertEqual(piece.created_at, legacy_created_at)
            self.assertLessEqual(
                piece.geom.num_coords, ZONE_PIECE_MAX_VERTICES
            )
        self.assertEqual(
            self.zone_set.zones.filter(feature_index=1).count(), 1
        )

        self.assertEqual(self._labels_on_grid(), before)

    def test_forward_matches_a_fresh_upload(self):
        """The migration and the helper cut a feature identically at
        the migration's budget."""
        self.helper.run_sql_file('0272_subdivide_zones.sql')
        migrated = [
            (zone.feature_index, zone.piece_index, zone.geom.ewkt)
            for zone in self.zone_set.zones.all()
        ]

        self.zone_set.replace_zones(subdivide_zone_records(
            records(
                feature(DISC, {'bws_label': 'High'}),
                feature(SQUARE, {'bws_label': 'Low'}),
            ),
            max_vertices=MIGRATION_BUDGET,
        ))
        uploaded = [
            (zone.feature_index, zone.piece_index, zone.geom.ewkt)
            for zone in self.zone_set.zones.all()
        ]

        self.assertEqual(migrated, uploaded)

    def test_reverse_merges_pieces_back_to_one_row_per_feature(self):
        original_area = self.zone_set.zones.get(feature_index=0).geom.area
        self.helper.run_sql_file('0272_subdivide_zones.sql')

        self.helper.run_sql_file('0272_revert_subdivide_zones.sql')

        zones = list(self.zone_set.zones.all())
        self.assertEqual(
            [(zone.feature_index, zone.piece_index) for zone in zones],
            [(0, 0), (1, 0)],
        )
        self.assertEqual(zones[0].label, 'High')
        self.assertAlmostEqual(zones[0].geom.area, original_area, places=9)
