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
    def test_bare_polygon(self):
        geojson = json.dumps({'type': 'Polygon', 'coordinates': SQUARE})
        result = parse_polygon_geojson(geojson)
        self.assertEqual(result.geom_type, 'MultiPolygon')
        self.assertEqual(len(result), 1)

    def test_polygon_with_hole_is_preserved(self):
        geojson = json.dumps(
            {'type': 'Polygon', 'coordinates': SQUARE_WITH_HOLE}
        )
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result[0]), 2)

    def test_bare_multipolygon(self):
        geojson = json.dumps({
            'type': 'MultiPolygon',
            'coordinates': [SQUARE, OTHER_SQUARE],
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(len(result), 2)

    def test_feature_is_unwrapped(self):
        geojson = json.dumps({
            'type': 'Feature',
            'properties': {},
            'geometry': {'type': 'Polygon', 'coordinates': SQUARE},
        })
        result = parse_polygon_geojson(geojson)
        self.assertEqual(result.geom_type, 'MultiPolygon')
        self.assertEqual(len(result), 1)

    def test_feature_collection_is_merged(self):
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
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson('not json')

    def test_non_polygon_geometry_raises(self):
        geojson = json.dumps({'type': 'Point', 'coordinates': [0, 0]})
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_feature_collection_with_no_geometries_raises(self):
        geojson = json.dumps({'type': 'FeatureCollection', 'features': []})
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_feature_collection_with_non_dict_feature_raises(self):
        geojson = json.dumps({
            'type': 'FeatureCollection',
            'features': [None, 'not a feature'],
        })
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def test_self_intersecting_polygon_raises(self):
        geojson = json.dumps(
            {'type': 'Polygon', 'coordinates': SELF_INTERSECTING}
        )
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_polygon_geojson(geojson)

    def _square_with_crs(self, crs):
        return json.dumps({
            'type': 'Polygon',
            'coordinates': SQUARE,
            'crs': crs,
        })

    def test_wgs84_crs_declarations_are_accepted(self):
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
        geojson = self._square_with_crs(
            {'type': 'name', 'properties': {'name': 'EPSG:32644'}}
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_polygon_geojson(geojson)
        message = str(ctx.exception)
        self.assertIn('EPSG:32644', message)
        self.assertIn('WGS 84', message)

    def test_malformed_crs_declaration_raises(self):
        for crs in ('EPSG:4326', {}, {'properties': {}}, 42):
            geojson = self._square_with_crs(crs)
            with self.assertRaises(InvalidPolygonGeoJSON):
                parse_polygon_geojson(geojson)

    def test_projected_coordinates_raise(self):
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
