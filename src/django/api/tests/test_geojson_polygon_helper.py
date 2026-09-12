import json
import unittest

from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_polygon_geojson,
)

SQUARE = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]
SQUARE_WITH_HOLE = [
    [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
    [[2, 2], [2, 4], [4, 4], [4, 2], [2, 2]],
]
OTHER_SQUARE = [[[20, 20], [20, 30], [30, 30], [30, 20], [20, 20]]]

SELF_INTERSECTING = [
    [[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]
]


class ParsePolygonGeoJSONTest(unittest.TestCase):
    """Tests for the GeoJSON-to-MultiPolygon parsing helper."""
    def test_bare_polygon(self):
        """A bare Polygon geometry parses into a one-part MultiPolygon."""
        geojson = json.dumps({'type': 'Polygon', 'coordinates': SQUARE})
        result = parse_polygon_geojson(geojson)
        self.assertEqual(result.geom_type, 'MultiPolygon')
        self.assertEqual(len(result), 1)

    def test_polygon_with_hole_is_preserved(self):
        """Interior rings (holes) survive parsing intact."""
        geojson = json.dumps(
            {'type': 'Polygon', 'coordinates': SQUARE_WITH_HOLE}
        )
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result[0]), 2)

    def test_bare_multipolygon(self):
        """A bare MultiPolygon keeps all of its parts."""
        geojson = json.dumps({
            'type': 'MultiPolygon',
            'coordinates': [SQUARE, OTHER_SQUARE],
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result), 2)

    def test_feature_is_unwrapped(self):
        """A Feature wrapper is unwrapped to its inner geometry."""
        geojson = json.dumps({
            'type': 'Feature',
            'properties': {},
            'geometry': {'type': 'Polygon', 'coordinates': SQUARE},
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(result.geom_type, 'MultiPolygon')
        self.assertEqual(len(result), 1)

    def test_feature_collection_is_merged(self):
        """A FeatureCollection's geometries merge into one MultiPolygon."""
        geojson = json.dumps({
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {'type': 'Polygon', 'coordinates': SQUARE},
                },
                {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'Polygon', 'coordinates': OTHER_SQUARE
                    },
                },
            ],
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result), 2)

    def test_invalid_json_raises(self):
        """Non-JSON input is rejected with a friendly error."""
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson('not json')

    def test_non_polygon_geometry_raises(self):
        """Non-polygon geometry (e.g. a Point) is rejected."""
        geojson = json.dumps({'type': 'Point', 'coordinates': [0, 0]})
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_feature_collection_with_no_geometries_raises(self):
        """A FeatureCollection with no usable geometry is rejected."""
        geojson = json.dumps({'type': 'FeatureCollection', 'features': []})
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_feature_collection_with_non_dict_feature_raises(self):
        """Malformed feature entries are rejected, not crashed on."""
        geojson = json.dumps({
            'type': 'FeatureCollection',
            'features': [None, 'not a feature'],
        })
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_self_intersecting_polygon_raises(self):
        """Self-intersecting (invalid) shapes are rejected."""
        geojson = json.dumps(
            {'type': 'Polygon', 'coordinates': SELF_INTERSECTING}
        )
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def _square_with_crs(self, crs):
        """Build square-polygon GeoJSON carrying the given crs member."""
        return json.dumps({
            'type': 'Polygon',
            'coordinates': SQUARE,
            'crs': crs,
        })

    def test_wgs84_crs_declarations_are_accepted(self):
        """Common WGS 84 spellings in a crs member are all accepted."""
        for name in (
            'urn:ogc:def:crs:OGC:1.3:CRS84',
            'EPSG:4326',
            'urn:ogc:def:crs:EPSG::4326',
        ):
            geojson = self._square_with_crs(
                {'type': 'name', 'properties': {'name': name}}
            )
            result = parse_polygon_geojson(geojson)
            self.assertEqual(result.geom_type, 'MultiPolygon')

    def test_non_wgs84_crs_declaration_raises(self):
        """A declared non-WGS-84 coordinate system is rejected, naming it."""
        geojson = self._square_with_crs(
            {'type': 'name', 'properties': {'name': 'EPSG:32644'}}
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_polygon_geojson(geojson)
        message = str(ctx.exception)
        self.assertIn('EPSG:32644', message)
        self.assertIn('WGS 84', message)

    def test_malformed_crs_declaration_raises(self):
        """A crs member we cannot interpret is rejected, not ignored."""
        for crs in ('EPSG:4326', {}, {'properties': {}}, 42):
            geojson = self._square_with_crs(crs)
            with self.assertRaises(InvalidPolygonGeoJSON):
                parse_polygon_geojson(geojson)

    def test_projected_coordinates_raise(self):
        """Meter-scale coordinates (undeclared projection) are rejected."""
        # Values like these are meters in a projected coordinate
        # system, not degrees; they must be rejected, not stored.
        geojson = json.dumps({
            'type': 'Polygon',
            'coordinates': [[
                [233000, 4210000],
                [233000, 4220000],
                [243000, 4220000],
                [243000, 4210000],
                [233000, 4210000],
            ]],
        })
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_polygon_geojson(geojson)
        self.assertIn('projected', str(ctx.exception))

    def test_full_world_extent_is_accepted(self):
        """Coordinates exactly at the lon/lat limits are still valid."""
        geojson = json.dumps({
            'type': 'Polygon',
            'coordinates': [[
                [-180, -90],
                [-180, 90],
                [180, 90],
                [180, -90],
                [-180, -90],
            ]],
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(result.geom_type, 'MultiPolygon')

    def test_empty_geometry_raises(self):
        """A geometry with no coordinates is rejected, not saved as a
        match-nothing boundary."""
        for coordinates in ([], [[]]):
            geojson = json.dumps({
                'type': 'MultiPolygon',
                'coordinates': coordinates,
            })
            with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
                parse_polygon_geojson(geojson)
            self.assertIn('no polygon coordinates', str(ctx.exception))

    def test_touching_features_are_merged_not_rejected(self):
        """Adjacent features sharing an edge (like neighboring
        districts) merge into one piece instead of being wrongly
        rejected as invalid."""
        left = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]
        right = [[[10, 0], [10, 10], [20, 10], [20, 0], [10, 0]]]
        geojson = json.dumps({
            'type': 'FeatureCollection',
            'features': [
                {'type': 'Feature', 'properties': {},
                 'geometry': {'type': 'Polygon', 'coordinates': left}},
                {'type': 'Feature', 'properties': {},
                 'geometry': {'type': 'Polygon', 'coordinates': right}},
            ],
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result), 1)
        # The merged piece covers both original squares.
        self.assertAlmostEqual(result.area, 200.0)

    def test_enclosed_gaps_stay_unmapped(self):
        """Merging touching pieces never fills space neither piece
        claimed. Two pieces that wrap around an enclave (think South
        Africa surrounding Lesotho) merge into one piece with a hole
        where the enclave is — the enclave stays outside the boundary.
        """
        # A donut split into two halves that touch along the split:
        # together they surround, but do not cover, the 3..7 square.
        left = [[[0, 0], [5, 0], [5, 3], [3, 3], [3, 7], [5, 7],
                 [5, 10], [0, 10], [0, 0]]]
        right = [[[5, 0], [10, 0], [10, 10], [5, 10], [5, 7], [7, 7],
                  [7, 3], [5, 3], [5, 0]]]
        geojson = json.dumps({
            'type': 'FeatureCollection',
            'features': [
                {'type': 'Feature', 'properties': {},
                 'geometry': {'type': 'Polygon', 'coordinates': left}},
                {'type': 'Feature', 'properties': {},
                 'geometry': {'type': 'Polygon', 'coordinates': right}},
            ],
        })
        result = parse_polygon_geojson(geojson)

        self.assertEqual(len(result), 1)      # merged into one piece
        self.assertEqual(len(result[0]), 2)   # outer ring + the hole
        from django.contrib.gis.geos import Point
        self.assertFalse(result.contains(Point(5, 5)))  # the "Lesotho"
        self.assertTrue(result.contains(Point(1, 1)))   # covered land

    def test_nested_crs_declarations_are_checked(self):
        """A non-WGS-84 coordinate-system label hidden inside a
        feature or geometry is rejected just like a top-level one."""
        bad_crs = {'type': 'name', 'properties': {'name': 'EPSG:32644'}}
        nested_in_feature = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature', 'properties': {}, 'crs': bad_crs,
                'geometry': {'type': 'Polygon', 'coordinates': SQUARE},
            }],
        }
        nested_in_geometry = {
            'type': 'Feature', 'properties': {},
            'geometry': {'type': 'Polygon', 'coordinates': SQUARE,
                         'crs': bad_crs},
        }
        for payload in (nested_in_feature, nested_in_geometry):
            with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
                parse_polygon_geojson(json.dumps(payload))
            self.assertIn('EPSG:32644', str(ctx.exception))
