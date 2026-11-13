from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_feature_collection_polygons,
)


def is_usable_zone_value(value):
    """
    Decide whether a feature property can serve as a zone's value.

    Only scalars make sense as a displayed value: strings (not blank),
    numbers, and booleans (a yes/no dataset such as "inside a
    floodplain" is legitimate). A missing or null value, a blank
    string, or a nested object or list counts as missing, so an upload
    is refused rather than showing an empty value or a Python repr on
    the page, and a stored property that fails this test is never
    served (see `ZoneSetProvider`).
    """
    if value is None or isinstance(value, (dict, list)):
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def parse_zone_features(raw, value_property=None, schema=None):
    """
    Parse a zoned GeoJSON FeatureCollection into zone records.

    Each feature becomes one zone: its geometry (kept separate, not
    dissolved with its neighbors) plus the value(s) read from its
    properties. The whole file is validated before anything is
    returned, so a caller that saves the result never saves a partial
    set.

    Two shapes, decided by the partner field the set feeds (see
    `ZoneSet.feeds_object_field`):

    - String field (`value_property` given, `schema` None): every
      feature must carry the chosen property with a usable scalar
      value, which becomes the zone's label.
    - Object field (`schema` given; `value_property` ignored): the
      zone is filled one feature property per key of the schema's
      `properties`, matched by name. Every feature must carry every
      key the schema's `required` array lists, with a usable scalar
      value; keys in the schema but not required may be absent. The
      label is the first required property's value, or empty when the
      schema requires nothing, so the admin's label summary and the
      Zones listing still show something recognisable. Properties
      outside the schema are kept (the full properties dict is stored
      so a zone can be traced to its source row) but never served.

    Args:
        raw: The GeoJSON FeatureCollection, as a string.
        value_property: The feature property key that supplies each
            zone's value for a string field (e.g. `bws_label` in
            Aqueduct exports).
        schema: The linked object field's JSON schema, a dict with a
            `properties` map and optionally a `required` list.

    Returns:
        A list of dicts, in file order, each with:
            - `geom`: a WGS 84 MultiPolygon
            - `label`: the zone's display label, as a string
            - `properties`: the feature's full properties dict

    Raises:
        InvalidPolygonGeoJSON: If the file fails geometry validation,
            or any feature lacks a property it must carry (the message
            names the key and says how many features are affected).
    """
    if schema is None:
        value_property = (value_property or '').strip()
        if not value_property:
            raise InvalidPolygonGeoJSON(
                'Choose which feature property supplies the zone value.'
            )

    features = parse_feature_collection_polygons(raw)

    if schema is None:
        problem = _missing_property_message(features, value_property)
        if problem:
            raise InvalidPolygonGeoJSON(
                f'{problem}. Every feature must carry a text, number or '
                'true/false value.'
            )
        return [
            {
                'geom': geom,
                'label': str(properties[value_property]),
                'properties': properties,
            }
            for geom, properties in features
        ]

    required = [
        key for key in (schema.get('required') or [])
        if isinstance(key, str)
    ]
    problems = []
    for key in required:
        problem = _missing_property_message(features, key)
        if problem:
            problems.append(problem)
    if problems:
        raise InvalidPolygonGeoJSON(
            '; '.join(problems) + '. Every feature must carry a text, '
            "number or true/false value for each property the field's "
            'schema lists as required.'
        )
    label_key = required[0] if required else None
    return [
        {
            'geom': geom,
            'label': str(properties[label_key]) if label_key else '',
            'properties': properties,
        }
        for geom, properties in features
    ]


def _missing_property_message(features, key):
    """
    Describe the features that lack a usable value for `key`, or
    return None when every feature carries one.
    """
    missing = [
        index for index, (_, properties) in enumerate(features)
        if not is_usable_zone_value(properties.get(key))
    ]
    if not missing:
        return None
    return (
        f'{len(missing)} of {len(features)} feature(s) are missing the '
        f'"{key}" property or have a blank or non-scalar value for it '
        f'(first at position {missing[0]})'
    )
