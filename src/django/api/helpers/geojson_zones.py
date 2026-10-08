from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_feature_collection_polygons,
)


def _is_usable_value(value):
    """
    Decide whether a feature property can serve as a zone's value.

    Only scalars make sense as a displayed label: strings (not blank),
    numbers, and booleans (a yes/no dataset such as "inside a
    floodplain" is legitimate). A missing or null value, a blank
    string, or a nested object or list counts as missing, so the
    upload is refused rather than showing an empty value or a Python
    repr on the page.
    """
    if value is None or isinstance(value, (dict, list)):
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def parse_zone_features(raw, value_property):
    """
    Parse a zoned GeoJSON FeatureCollection into zone records.

    Each feature becomes one zone: its geometry (kept separate, not
    dissolved with its neighbours) plus the value read from the chosen
    feature property. The whole file is validated before anything is
    returned, so a caller that saves the result never saves a partial
    set.

    Args:
        raw: The GeoJSON FeatureCollection, as a string.
        value_property: The feature property key that supplies each
            zone's value (e.g. `bws_label` in Aqueduct exports).

    Returns:
        A list of dicts, in file order, each with:
            - `geom`: a WGS 84 MultiPolygon
            - `label`: the zone's display label (the chosen property,
              as a string)
            - `properties`: the feature's full properties dict, kept
              so a zone can be traced back to its source row

    Raises:
        InvalidPolygonGeoJSON: If the file fails geometry validation,
            or any feature lacks the chosen property (the message says
            how many).
    """
    value_property = (value_property or '').strip()
    if not value_property:
        raise InvalidPolygonGeoJSON(
            'Choose which feature property supplies the zone value.'
        )

    features = parse_feature_collection_polygons(raw)

    missing = [
        index for index, (_, properties) in enumerate(features)
        if not _is_usable_value(properties.get(value_property))
    ]
    if missing:
        raise InvalidPolygonGeoJSON(
            f'{len(missing)} of {len(features)} feature(s) are missing '
            f'the "{value_property}" property or have a blank or '
            f'non-scalar value for it (first at position {missing[0]}). '
            'Every feature must carry a text, number or true/false value.'
        )

    return [
        {
            'geom': geom,
            'label': str(properties[value_property]),
            'properties': properties,
        }
        for geom, properties in features
    ]
