import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon


class InvalidPolygonGeoJSON(ValueError):
    """Raised when a string cannot be parsed into a valid polygon."""


REEXPORT_ADVICE = (
    'Please re-export the data in WGS 84 (EPSG:4326) and try again.'
)

# Spellings of WGS 84 accepted in a legacy GeoJSON `crs` member.
# Current GeoJSON (RFC 7946) removed `crs` entirely — WGS 84 is the
# only coordinate system the spec allows — but older files and some GIS
# tools still write the member, so when it is present we check that it
# names WGS 84 and reject anything else before parsing.
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
    """
    Reject GeoJSON that declares a coordinate system other than WGS 84.

    OS Hub stores all coordinates in WGS 84 (EPSG:4326). If a file
    declares a different coordinate system, its numbers mean something
    else entirely (often meters in a projected grid), and storing them
    unconverted would silently place the boundary in the wrong spot on
    Earth — so we stop it here with instructions instead.

    Args:
        data: The parsed top-level GeoJSON dict. A missing `crs` member
            is fine (the spec's default is WGS 84); a `crs` member that
            names WGS 84 in any common spelling is fine; anything else
            raises.

    Raises:
        InvalidPolygonGeoJSON: If `crs` is present but malformed, or
            names a non-WGS-84 coordinate system.
    """
    crs = data.get('crs')
    if crs is None:
        # No declared coordinate system. This is the normal, spec-
        # compliant case: current GeoJSON has no `crs` member at all
        # and is always WGS 84, so there is nothing to check.
        return

    # A well-formed legacy declaration looks like:
    #   {"type": "name", "properties": {"name": "EPSG:4326"}}
    # Dig the name out defensively — a malformed member is treated as
    # an error rather than being ignored, since we can't know what
    # coordinate system the file intended.
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
    """
    Reject geometry whose coordinates cannot be longitude/latitude.

    This catches the sneakier cousin of the `_check_crs` case: a file
    whose coordinates are in a projected system (meters, so values like
    233000) but which declares no coordinate system at all. Such values
    fall far outside the valid longitude (±180) and latitude (±90)
    ranges, so a simple bounds check exposes them.

    Args:
        geom: The parsed GEOS geometry to check.

    Raises:
        InvalidPolygonGeoJSON: If any part of the geometry's bounding
            box falls outside valid longitude/latitude ranges.
    """
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

    Along the way this rejects, with a human-readable message: invalid
    JSON, non-polygon geometry, self-intersecting or otherwise invalid
    shapes, declared non-WGS-84 coordinate systems, and coordinates
    outside valid longitude/latitude ranges.

    Args:
        raw: The GeoJSON, as a string (e.g. pasted text or the decoded
            contents of an uploaded file).

    Returns:
        A GEOS `MultiPolygon` in WGS 84 (EPSG:4326), ready to assign to
        a geometry model field.

    Raises:
        InvalidPolygonGeoJSON: If the input cannot be turned into a
            valid polygon boundary, with a message suitable for showing
            directly to admin users.
    """
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise InvalidPolygonGeoJSON(f'Not valid JSON: {exc}') from exc

    if isinstance(data, dict):
        _check_crs(data)

    geom_type = data.get('type') if isinstance(data, dict) else None

    # Unwrap down to a list of plain geometry dicts, whichever of the
    # three accepted GeoJSON shapes we were given.
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

    # Parse each geometry and flatten everything into one list of
    # simple polygons (MultiPolygons contribute each of their parts).
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
