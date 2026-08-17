import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon


class InvalidPolygonGeoJSON(ValueError):
    """Raised when a string cannot be parsed into a valid polygon."""


def parse_polygon_geojson(raw):
    """
    Parse a GeoJSON string into a single valid MultiPolygon in EPSG:4326.

    Accepts a bare Polygon or MultiPolygon geometry, a Feature wrapping
    one of those geometries, or a FeatureCollection whose features'
    geometries are combined into one MultiPolygon. Polygons may have
    holes; any number of disjoint polygons is supported.
    """
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise InvalidPolygonGeoJSON(f'Not valid JSON: {exc}') from exc

    geom_type = data.get('type') if isinstance(data, dict) else None

    if geom_type == 'FeatureCollection':
        geometries = [
            feature['geometry']
            for feature in (data.get('features') or [])
            if isinstance(feature, dict) and feature.get('geometry')
            is not None
        ]
        if not geometries:
            raise InvalidPolygonGeoJSON(
                'FeatureCollection has no features with a geometry.'
            )
    elif geom_type == 'Feature':
        geometry = data.get('geometry')
        if geometry is None:
            raise InvalidPolygonGeoJSON('Feature has no geometry.')
        geometries = [geometry]
    else:
        geometries = [data]

    polygons = []
    for geometry in geometries:
        try:
            geom = GEOSGeometry(json.dumps(geometry))
        except (GEOSException, ValueError, TypeError) as exc:
            raise InvalidPolygonGeoJSON(
                f'Could not parse geometry: {exc}'
            ) from exc

        if geom.geom_type == 'Polygon':
            polygons.append(geom)
        elif geom.geom_type == 'MultiPolygon':
            polygons.extend(geom)
        else:
            raise InvalidPolygonGeoJSON(
                'Expected a Polygon or MultiPolygon geometry, got '
                f'{geom.geom_type}.'
            )

    result = MultiPolygon(*polygons, srid=4326)

    if not result.valid:
        raise InvalidPolygonGeoJSON(
            f'Geometry is not valid: {result.valid_reason}'
        )

    return result
