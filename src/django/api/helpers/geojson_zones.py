from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_feature_collection_polygons,
)


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
        if properties.get(value_property) is None
    ]
    if missing:
        raise InvalidPolygonGeoJSON(
            f'{len(missing)} of {len(features)} feature(s) are missing '
            f'the "{value_property}" property (first at position '
            f'{missing[0]}). Every feature must carry it.'
        )

    return [
        {
            'geom': geom,
            'label': str(properties[value_property]),
            'properties': properties,
        }
        for geom, properties in features
    ]
