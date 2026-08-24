import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon


class InvalidPolygonGeoJSON(ValueError):
    """Raised when a string cannot be parsed into a valid polygon."""


REEXPORT_ADVICE = (
    'Please re-export the data in WGS 84 (EPSG:4326) and try again.'
)

# The different ways a GeoJSON file might spell out "WGS 84" — the
# standard latitude/longitude system OS Hub uses. Modern GeoJSON files
# don't name a coordinate system at all (WGS 84 is simply the rule),
# but older files and some mapping tools still include a label. When a
# label is present, we accept only these spellings.
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

    OS Hub stores every coordinate as plain latitude/longitude
    (WGS 84). If a file says its numbers are in some other coordinate
    system, then those numbers aren't latitudes and longitudes at all —
    often they're meters on a map grid — and saving them as-is would
    quietly put the boundary in the wrong place on the map. Better to
    stop here and tell the person how to fix the file.

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

    # A well-formed label looks like:
    #   {"type": "name", "properties": {"name": "EPSG:4326"}}
    # If the label doesn't have that shape, we can't tell what
    # coordinate system the file meant — so that's an error too,
    # rather than something to quietly ignore.
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

    Some files use map-grid coordinates measured in meters (values
    like 233000) without labeling the coordinate system, so the label
    check in `_check_crs` never sees them. Meter values sit far
    outside the possible range for longitude (-180 to 180) and
    latitude (-90 to 90), so checking the ranges catches these files.

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


def _extract_geometries(data):
    """
    Unwrap the accepted GeoJSON shapes into a list of geometry dicts.

    Handles the three shapes we accept: a FeatureCollection (take each
    feature's geometry), a Feature (take its geometry), or a bare
    geometry (use it as-is).

    Args:
        data: The parsed GeoJSON.

    Raises:
        InvalidPolygonGeoJSON: If a Feature or FeatureCollection turns
            out to contain no geometry at all.
    """
    geom_type = data.get('type') if isinstance(data, dict) else None

    if geom_type == 'FeatureCollection':
        features = [
            feature for feature in (data.get('features') or [])
            if isinstance(feature, dict) and feature.get('geometry')
            is not None
        ]
        # A coordinate-system label can also appear on an individual
        # feature, not just at the top level — check those too, so a
        # non-WGS-84 label can't slip in nested.
        for feature in features:
            _check_crs(feature)
        geometries = [feature['geometry'] for feature in features]
        if not geometries:
            raise InvalidPolygonGeoJSON(
                'FeatureCollection has no features with a geometry.'
            )
        return geometries

    if geom_type == 'Feature':
        geometry = data.get('geometry')
        if geometry is None:
            raise InvalidPolygonGeoJSON('Feature has no geometry.')
        return [geometry]

    return [data]


def _parse_polygons(geometries):
    """
    Parse geometry dicts into a flat list of simple polygons.

    MultiPolygons contribute each of their parts to the list, so the
    caller can combine everything into one MultiPolygon at the end.

    Args:
        geometries: A list of GeoJSON geometry dicts.

    Raises:
        InvalidPolygonGeoJSON: If a geometry cannot be parsed, or is
            something other than a Polygon or MultiPolygon.
    """
    polygons = []
    for geometry in geometries:
        # Geometry objects themselves can carry a coordinate-system
        # label in older files; reject non-WGS-84 ones here too.
        if isinstance(geometry, dict):
            _check_crs(geometry)
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
    return polygons


def _combine_polygons(polygons):
    """
    Merge simple polygons into one MultiPolygon, dissolving shared
    borders.

    Real regional exports are often several features that touch along
    their edges (neighboring districts, for example). Simply stapling
    those together makes a technically-invalid shape even though
    nothing is wrong with the file — so instead, touching or
    overlapping pieces are merged into one, and separate pieces are
    kept separate. Each piece is checked for validity on its own
    first, so a shape that genuinely crosses over itself is still
    rejected with a message about that shape.

    Args:
        polygons: Simple GEOS polygons from `_parse_polygons`.

    Raises:
        InvalidPolygonGeoJSON: If there are no polygons, a polygon is
            individually invalid, or the merged result is empty or
            invalid.
    """
    # No coordinates at all (e.g. a MultiPolygon with an empty
    # coordinates list) would save a boundary that matches nothing.
    if not polygons:
        raise InvalidPolygonGeoJSON(
            'The GeoJSON contains no polygon coordinates.'
        )

    for polygon in polygons:
        if not polygon.valid:
            raise InvalidPolygonGeoJSON(
                f'Geometry is not valid: {polygon.valid_reason}'
            )

    combined = polygons[0]
    for polygon in polygons[1:]:
        combined = combined.union(polygon)

    if combined.geom_type == 'Polygon':
        combined = MultiPolygon(combined)
    combined.srid = 4326

    if combined.empty or combined.num_coords == 0:
        raise InvalidPolygonGeoJSON(
            'The GeoJSON contains no polygon coordinates.'
        )

    if not combined.valid:
        raise InvalidPolygonGeoJSON(
            f'Geometry is not valid: {combined.valid_reason}'
        )

    return combined


def parse_polygon_geojson(raw):
    """
    Turn a GeoJSON string into one valid MultiPolygon in WGS 84.

    Different mapping tools wrap the same shape in different ways — a
    bare Polygon or MultiPolygon, a Feature around one of those, or a
    FeatureCollection holding several. All three are accepted so staff
    can paste or upload whatever their tool produced, without hand-
    editing files first. Shapes with holes, and boundaries made of
    several separate pieces, are supported for the same reason: real
    boundaries look like that. Pieces that touch or overlap (such as
    neighboring districts exported together) are merged into one.

    Bad input is rejected with a message written for the person using
    the admin form. That covers: broken JSON, geometry that isn't a
    polygon, shapes that cross over themselves, empty shapes, a
    declared non-WGS-84 coordinate system, and coordinates outside the
    possible longitude/latitude ranges.

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

    geometries = _extract_geometries(data)
    polygons = _parse_polygons(geometries)

    result = _combine_polygons(polygons)

    _check_bounds(result)

    return result
