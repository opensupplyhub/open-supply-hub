import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon


class InvalidPolygonGeoJSON(ValueError):
    """Raised when a string cannot be parsed into a valid polygon."""


REEXPORT_ADVICE = (
    'Please re-export the data in WGS 84 (EPSG:4326) and try again.'
)

# Spellings of WGS 84 accepted in a legacy GeoJSON `crs` member
# (RFC 7946 removed `crs`; WGS 84 is the only coordinate system the
# spec allows, so anything else must be rejected before parsing).
WGS84_CRS_NAMES = frozenset({
    'urn:ogc:def:crs:ogc:1.3:crs84',
    'urn:ogc:def:crs:ogc:2:84',
    'urn:ogc:def:crs:epsg::4326',
    'crs84',
    'epsg:4326',
    'wgs84',
    'wgs 84',
})


def _check_crs(data):
    crs = data.get('crs')
    if crs is None:
        return

    name = None
    if isinstance(crs, dict):
        properties = crs.get('properties')
        if isinstance(properties, dict):
            name = properties.get('name')

    if not isinstance(name, str):
        raise InvalidPolygonGeoJSON(
            'This GeoJSON declares a coordinate system in a format '
            f'that could not be understood. {REEXPORT_ADVICE}'
        )

    if name.strip().lower() not in WGS84_CRS_NAMES:
        raise InvalidPolygonGeoJSON(
            'This GeoJSON declares a coordinate system other than '
            f'WGS 84 (found: {name}). {REEXPORT_ADVICE}'
        )


def _check_bounds(geom):
    xmin, ymin, xmax, ymax = geom.extent
    if xmin < -180 or xmax > 180 or ymin < -90 or ymax > 90:
        raise InvalidPolygonGeoJSON(
            'Coordinates fall outside the valid longitude/latitude '
            f'ranges (bounds found: {xmin:g} {ymin:g} to '
            f'{xmax:g} {ymax:g}). This usually means the file uses a '
            f'projected coordinate system. {REEXPORT_ADVICE}'
        )


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

    if isinstance(data, dict):
        _check_crs(data)

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

    _check_bounds(result)

    return result
