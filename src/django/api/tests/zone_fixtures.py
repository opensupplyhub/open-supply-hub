"""
GeoJSON fixtures shared by the zone-set tests (the admin form, the
subdivision helper and the migration that re-cuts existing zones), so
every suite exercises the same shapes.
"""
import json
import math

from django.core.files.uploadedfile import SimpleUploadedFile

from api.helpers.geojson_zones import parse_zone_features


def ring(center_x, center_y, radius, vertices):
    """A closed ring approximating a circle with the given vertex count."""
    coords = [
        [
            center_x + radius * math.cos(2 * math.pi * i / vertices),
            center_y + radius * math.sin(2 * math.pi * i / vertices),
        ]
        for i in range(vertices)
    ]
    return coords + [coords[0]]


# A single feature well over the vertex budget (a 600-vertex disc),
# stored as several pieces (see api.helpers.zone_subdivision).
DISC = [ring(50, 50, 20, 600)]


def feature(coordinates, properties):
    """A GeoJSON Polygon Feature."""
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {'type': 'Polygon', 'coordinates': coordinates},
    }


def collection(*features):
    """A GeoJSON FeatureCollection, as the string a file would hold."""
    return json.dumps({'type': 'FeatureCollection', 'features': features})


def upload(*features, name='zones.geojson'):
    """Build an uploaded FeatureCollection file."""
    return SimpleUploadedFile(
        name, collection(*features).encode('utf-8'),
        content_type='application/geo+json',
    )


def records(*features, value_property='bws_label'):
    """The parsed zone records for the features, as the form sees them."""
    return parse_zone_features(collection(*features), value_property)
