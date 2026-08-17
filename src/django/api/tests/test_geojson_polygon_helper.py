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
