'''
Pure helpers for interpreting a PartnerField definition against the
`extended_fields` payload stored on FacilityIndex.

These helpers are kept outside the serializer classes because they carry
no serializer state and can be exercised in isolation. The download
serializer composes them from its own `get_partner_fields_headers` and
`get_partner_fields_row` methods, keeping the surface of the serializer
consistent with `get_extended_fields`, `get_claimed_fields`, etc.
'''
from typing import Any, Dict, List, Tuple

from api.models.partner_field import PartnerField


def partner_field_property_paths(
    partner_field: PartnerField,
) -> List[Tuple[str, ...]]:
    '''
    Return the list of leaf property paths defined in a partner
    field's JSON Schema. Each path is a tuple of property keys from
    the schema root down to the leaf. Returns an empty list for
    partner fields that are not object-typed or do not declare a
    usable schema, in which case callers fall back to the partner
    field name itself as a single column.
    '''
    if partner_field.type != PartnerField.OBJECT:
        return []
    schema = partner_field.json_schema or {}
    return collect_leaf_paths(schema)


def collect_leaf_paths(
    schema: Dict[str, Any],
    prefix: Tuple[str, ...] = (),
) -> List[Tuple[str, ...]]:
    '''
    Walk a JSON Schema and return every leaf path as a tuple of keys.

    A property is considered a leaf when it is not an object type, or
    when it is an object but declares no nested `properties`. Nested
    object schemas are expanded recursively in declaration order.
    '''
    properties = (schema or {}).get("properties") or {}
    if not properties:
        return [prefix] if prefix else []

    paths: List[Tuple[str, ...]] = []
    for key, sub_schema in properties.items():
        sub_schema = sub_schema or {}
        next_prefix = (*prefix, key)
        is_object = sub_schema.get("type") == PartnerField.OBJECT
        nested_props = sub_schema.get("properties") or {}
        if is_object and nested_props:
            paths.extend(collect_leaf_paths(sub_schema, next_prefix))
        else:
            paths.append(next_prefix)
    return paths


def resolve_nested_value(
    raw_values: Dict[str, Any],
    path: Tuple[str, ...],
) -> Any:
    '''
    Follow `path` through a nested `raw_values` dict and return the
    value at the leaf, or None if any segment is missing or the
    intermediate value is not a dict.
    '''
    current: Any = raw_values
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def group_extended_fields_by_name(
    extended_fields: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    '''
    Bucket FacilityIndex.extended_fields entries by their `field_name`
    so partner fields can look up matching contributions in O(1).
    '''
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in extended_fields or []:
        name = entry.get("field_name")
        if name:
            grouped.setdefault(name, []).append(entry)
    return grouped


def is_empty_partner_value(value: Any) -> bool:
    '''Treat None and empty strings as "no value" for CSV cells.'''
    return value is None or value == ""
