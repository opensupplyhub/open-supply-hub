import json
import unittest

from django.contrib.gis.geos import Point

from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_feature_collection_polygons,
)
from api.helpers.geojson_zones import parse_zone_features

LEFT = [[[0, 0], [0, 10], [5, 10], [5, 0], [0, 0]]]
RIGHT = [[[5, 0], [5, 10], [10, 10], [10, 0], [5, 0]]]
FAR = [[[20, 20], [20, 30], [30, 30], [30, 20], [20, 20]]]


def feature(coordinates, properties, geom_type='Polygon', **extra):
    """Build one GeoJSON Feature dict."""
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {'type': geom_type, 'coordinates': coordinates},
        **extra,
    }


def collection(*features, **extra):
    """Build a GeoJSON FeatureCollection string."""
    return json.dumps({
        'type': 'FeatureCollection', 'features': list(features), **extra,
    })


class ParseFeatureCollectionPolygonsTest(unittest.TestCase):
    """Tests for the per-feature parser the zone ingestor builds on."""

    def test_features_stay_separate(self):
        """Touching features are NOT dissolved — each keeps its own
        geometry and properties, unlike the single-boundary parser."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High'}),
            feature(RIGHT, {'bws_label': 'Low'}),
        )

        result = parse_feature_collection_polygons(raw)

        self.assertEqual(len(result), 2)
        (left_geom, left_props), (right_geom, right_props) = result
        self.assertEqual(left_props, {'bws_label': 'High'})
        self.assertEqual(right_props, {'bws_label': 'Low'})
        self.assertEqual(left_geom.geom_type, 'MultiPolygon')
        self.assertEqual(left_geom.srid, 4326)
        self.assertTrue(left_geom.contains(Point(2, 5)))
        self.assertFalse(left_geom.contains(Point(8, 5)))
        self.assertTrue(right_geom.contains(Point(8, 5)))

    def test_multipolygon_feature_stays_one_zone(self):
        """A feature whose geometry is a MultiPolygon with disjoint
        parts becomes one zone covering both parts."""
        raw = collection(
            feature([LEFT, FAR], {'k': 'v'}, geom_type='MultiPolygon'),
        )

        [(geom, _)] = parse_feature_collection_polygons(raw)

        self.assertEqual(len(geom), 2)
        self.assertTrue(geom.contains(Point(2, 5)))
        self.assertTrue(geom.contains(Point(25, 25)))

    def test_missing_properties_become_empty_dict(self):
        """A feature with no `properties` member still parses."""
        raw = json.dumps({
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {'type': 'Polygon', 'coordinates': LEFT},
            }],
        })

        [(_, properties)] = parse_feature_collection_polygons(raw)

        self.assertEqual(properties, {})

    def test_rejects_non_feature_collection(self):
        """A bare geometry or Feature is not a zoned dataset."""
        bare = json.dumps({'type': 'Polygon', 'coordinates': LEFT})
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(bare)
        self.assertIn('FeatureCollection', str(ctx.exception))

    def test_rejects_invalid_json(self):
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_feature_collection_polygons('not json')

    def test_rejects_empty_collection(self):
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(collection())
        self.assertIn('no features', str(ctx.exception))

    def test_rejects_features_without_geometry_with_a_count(self):
        """Null-geometry features are counted and refused, since a
        zone with no shape could never match a location."""
        raw = json.dumps({
            'type': 'FeatureCollection',
            'features': [
                feature(LEFT, {}),
                {'type': 'Feature', 'properties': {}, 'geometry': None},
                {'type': 'Feature', 'properties': {}},
            ],
        })
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(raw)
        self.assertIn('2 feature(s) have no geometry', str(ctx.exception))
        self.assertIn('position 1', str(ctx.exception))

    def test_rejects_projected_crs_declaration(self):
        """A non-WGS-84 coordinate system, at the top level or on a
        feature, is rejected with advice to re-export."""
        bad_crs = {'type': 'name', 'properties': {'name': 'EPSG:32644'}}
        top_level = collection(feature(LEFT, {}), crs=bad_crs)
        on_feature = collection(feature(LEFT, {}, crs=bad_crs))
        for raw in (top_level, on_feature):
            with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
                parse_feature_collection_polygons(raw)
            self.assertIn('EPSG:32644', str(ctx.exception))

    def test_rejects_projected_coordinates_without_a_label(self):
        """Metre-valued coordinates fail the lon/lat bounds check and
        the message names the offending feature."""
        metres = [[[233000, 1500000], [233000, 1600000],
                   [333000, 1600000], [333000, 1500000],
                   [233000, 1500000]]]
        raw = collection(feature(LEFT, {}), feature(metres, {}))
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(raw)
        self.assertIn('Feature at position 1', str(ctx.exception))
        self.assertIn('projected coordinate system', str(ctx.exception))

    def test_rejects_invalid_geometry(self):
        """A self-intersecting ring is refused, naming the feature."""
        bowtie = [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]]
        raw = collection(feature(bowtie, {}))
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(raw)
        self.assertIn('Feature at position 0', str(ctx.exception))
        self.assertIn('not valid', str(ctx.exception))

    def test_rejects_non_polygon_geometry(self):
        raw = collection(feature([1, 1], {}, geom_type='Point'))
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_feature_collection_polygons(raw)
        self.assertIn('Point', str(ctx.exception))


class ParseZoneFeaturesTest(unittest.TestCase):
    """Tests for turning a FeatureCollection into zone records."""

    def test_reads_label_from_chosen_property(self):
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bws_score': 3.2}),
            feature(RIGHT, {'bws_label': 'Low', 'bws_score': 0.4}),
        )

        zones = parse_zone_features(raw, 'bws_label')

        self.assertEqual([zone['label'] for zone in zones], ['High', 'Low'])
        self.assertEqual(
            zones[0]['properties'], {'bws_label': 'High', 'bws_score': 3.2}
        )
        self.assertTrue(zones[1]['geom'].contains(Point(8, 5)))

    def test_numeric_values_become_strings(self):
        """A numeric property (a score, a class code) is still a
        usable display label."""
        raw = collection(feature(LEFT, {'cls': 4}))
        [zone] = parse_zone_features(raw, 'cls')
        self.assertEqual(zone['label'], '4')

    def test_counts_features_missing_the_property(self):
        """Missing or null values are refused with a count, per the
        ticket's acceptance criteria."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High'}),
            feature(RIGHT, {'other': 'x'}),
            feature(FAR, {'bws_label': None}),
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_zone_features(raw, 'bws_label')
        message = str(ctx.exception)
        self.assertIn('2 of 3 feature(s) are missing', message)
        self.assertIn('"bws_label"', message)
        self.assertIn('position 1', message)

    def test_requires_a_property_key(self):
        raw = collection(feature(LEFT, {'bws_label': 'High'}))
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_zone_features(raw, '  ')

    def test_geometry_errors_propagate(self):
        """Geometry validation runs before the property check, so a
        broken file is refused even when every property is present."""
        bowtie = [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]]
        raw = collection(feature(bowtie, {'bws_label': 'High'}))
        with self.assertRaises(InvalidPolygonGeoJSON):
            parse_zone_features(raw, 'bws_label')
