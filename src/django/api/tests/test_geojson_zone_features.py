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

    def test_blank_and_nested_values_count_as_missing(self):
        """An empty string would show an empty value on the page and a
        nested object would show as a Python repr, so both are refused
        alongside genuinely missing values."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High'}),
            feature(RIGHT, {'bws_label': '   '}),
            feature(FAR, {'bws_label': {'nested': 1}}),
            feature(LEFT, {'bws_label': ['a', 'b']}),
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_zone_features(raw, 'bws_label')
        message = str(ctx.exception)
        self.assertIn('3 of 4 feature(s)', message)
        self.assertIn('blank or non-scalar', message)
        self.assertIn('position 1', message)

    def test_boolean_values_are_usable_labels(self):
        """A yes/no dataset (e.g. inside a floodplain) is legitimate."""
        raw = collection(
            feature(LEFT, {'flood': True}),
            feature(RIGHT, {'flood': False}),
        )
        zones = parse_zone_features(raw, 'flood')
        self.assertEqual([zone['label'] for zone in zones], ['True', 'False'])

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


# The schema of an object partner field such as the Aqueduct block:
# two required labels and an optional link.
SCHEMA = {
    'type': 'object',
    'properties': {
        'bws_label': {'type': 'string', 'title': 'Water stress, today'},
        'bwd_label': {'type': 'string', 'title': 'Drought risk'},
        'atlas_url': {
            'type': 'string', 'format': 'uri',
            'title': 'Aqueduct Water Risk Atlas',
        },
    },
    'required': ['bws_label', 'bwd_label'],
}


class ParseZoneFeaturesForObjectFieldTest(unittest.TestCase):
    """Tests for reading zones for an object-type partner field, one
    feature property per schema key (OSDEV-3659)."""

    def test_reads_required_keys_and_labels_by_the_first(self):
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low',
                           'atlas_url': 'https://example.org/a'}),
            feature(RIGHT, {'bws_label': 'Low', 'bwd_label': 'High'}),
        )

        zones = parse_zone_features(raw, schema=SCHEMA)

        self.assertEqual([zone['label'] for zone in zones], ['High', 'Low'])
        self.assertEqual(
            zones[0]['properties'],
            {'bws_label': 'High', 'bwd_label': 'Low',
             'atlas_url': 'https://example.org/a'},
        )
        self.assertTrue(zones[1]['geom'].contains(Point(8, 5)))

    def test_optional_schema_keys_may_be_absent(self):
        """Only the `required` keys are checked; `atlas_url` is in the
        schema but not required, so a feature without it is fine."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
        )
        [zone] = parse_zone_features(raw, schema=SCHEMA)
        self.assertNotIn('atlas_url', zone['properties'])

    def test_properties_outside_the_schema_are_kept(self):
        """The full properties dict is stored so a zone can be traced
        to its source row; the provider decides what is served."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low',
                           'pfaf_id': 2345}),
        )
        [zone] = parse_zone_features(raw, schema=SCHEMA)
        self.assertEqual(zone['properties']['pfaf_id'], 2345)

    def test_counts_features_missing_a_required_key(self):
        """AC #3: the message names the key and how many features
        lack it, and reports every required key with a problem."""
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
            feature(RIGHT, {'bws_label': 'Low'}),
            feature(FAR, {'bwd_label': None, 'bws_label': '  '}),
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_zone_features(raw, schema=SCHEMA)
        message = str(ctx.exception)
        self.assertIn('1 of 3 feature(s) are missing the "bws_label"', message)
        self.assertIn('2 of 3 feature(s) are missing the "bwd_label"', message)
        self.assertIn('(first at position 1)', message)
        self.assertIn('lists as required', message)

    def test_nested_required_value_counts_as_missing(self):
        raw = collection(
            feature(LEFT, {'bws_label': {'nested': 1}, 'bwd_label': 'Low'}),
        )
        with self.assertRaises(InvalidPolygonGeoJSON) as ctx:
            parse_zone_features(raw, schema=SCHEMA)
        self.assertIn('blank or non-scalar', str(ctx.exception))

    def test_schema_without_required_keys_gives_an_empty_label(self):
        """Nothing is mandatory and nothing identifies the zone, so the
        label is empty rather than guessed from an arbitrary key."""
        schema = {'properties': {'note': {'type': 'string'}}}
        raw = collection(feature(LEFT, {}))
        [zone] = parse_zone_features(raw, schema=schema)
        self.assertEqual(zone['label'], '')

    def test_value_property_is_ignored_when_a_schema_is_given(self):
        raw = collection(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
        )
        [zone] = parse_zone_features(raw, 'not_a_key', schema=SCHEMA)
        self.assertEqual(zone['label'], 'High')
