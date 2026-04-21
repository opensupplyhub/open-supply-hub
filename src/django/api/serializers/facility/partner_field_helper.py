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

from django.core.cache import cache

from api.constants import (
    PARTNER_FIELD_LIST_CACHE_TTL_SECONDS,
    PARTNER_FIELD_LIST_KEY,
)
from api.models.partner_field import PartnerField


def get_cached_all_partner_fields() -> List[PartnerField]:
    '''
    Return every `PartnerField` row (active + inactive, user + system)
    from the shared `PARTNER_FIELD_LIST_KEY` cache, populating it with
    `PartnerField.objects.all()` on a miss.

    Callers that only want a subset (e.g. active, non-system fields for
    downloads) must filter the returned list in memory. All consumers
    must cache the same superset under this key so a warm cache written
    by one caller stays correct for every other caller — mixing
    pre-filtered lists under the same key causes silent data drift.
    `PartnerField.save`/`delete` invalidate the entry so updates and
    (in)activation flips are reflected in subsequent reads.
    '''
    cached = cache.get(PARTNER_FIELD_LIST_KEY)
    if cached is not None:
        return list(cached)

    partner_fields = list(
        PartnerField.objects.get_all_including_inactive()
    )
    cache.set(
        PARTNER_FIELD_LIST_KEY,
        partner_fields,
        PARTNER_FIELD_LIST_CACHE_TTL_SECONDS,
    )
    return partner_fields


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
    schema = partner_field.json_schema
    if not isinstance(schema, dict):
        return []
    return collect_leaf_paths(schema)


def collect_leaf_paths(
    schema: Dict[str, Any],
    prefix: Tuple[str, ...] = (),
) -> List[Tuple[str, ...]]:
    '''
    Walk a JSON Schema and return every leaf path as a tuple of keys.

    A node is treated as a branch (and recursed into) when it is a dict
    whose `properties` is a non-empty dict, regardless of whether the
    node explicitly declares `type: "object"` — this is lenient about
    hand-authored schemas that omit `type`. Any node that is not a
    dict, or whose `properties` is missing/empty/not a dict, is treated
    as a leaf, so a malformed `json_schema` gracefully falls back to a
    single partner-field column instead of crashing the whole download.
    '''
    if not isinstance(schema, dict):
        return [prefix] if prefix else []

    properties = schema.get("properties")
    if not isinstance(properties, dict) or not properties:
        return [prefix] if prefix else []

    paths: List[Tuple[str, ...]] = []
    for key, sub_schema in properties.items():
        next_prefix = (*prefix, key)
        if _has_nested_properties(sub_schema):
            paths.extend(collect_leaf_paths(sub_schema, next_prefix))
        else:
            paths.append(next_prefix)
    return paths


def _has_nested_properties(sub_schema: Any) -> bool:
    if not isinstance(sub_schema, dict):
        return False
    nested = sub_schema.get("properties")
    return isinstance(nested, dict) and bool(nested)


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
    Non-dict entries are skipped defensively so a malformed row in
    `facility.extended_fields` cannot take down the whole download page.
    '''
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in extended_fields or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("field_name")
        if name:
            grouped.setdefault(name, []).append(entry)
    return grouped


def is_empty_partner_value(value: Any) -> bool:
    '''Treat None and empty strings as "no value" for CSV cells.'''
    return value is None or value == ""


def _entry_value_dict(entry: Any) -> Dict[str, Any]:
    '''
    Return the `value` payload of an extended_fields entry as a dict,
    or an empty dict if the entry or its `value` is not a dict. This
    makes partner-field formatting tolerant of malformed rows (scalar
    or list `value` payloads) so a single bad contribution never fails
    the whole download page.
    '''
    if not isinstance(entry, dict):
        return {}
    value = entry.get("value")
    return value if isinstance(value, dict) else {}


def build_object_field_cells(
    entries: List[Dict[str, Any]],
    paths: List[Tuple[str, ...]],
    separator: str,
) -> List[str]:
    '''
    Build one joined cell per leaf path for an object-typed partner
    field, walking each contribution's `raw_values` in declaration
    order and skipping empty values.
    '''
    collected: Dict[Tuple[str, ...], List[str]] = {
        path: [] for path in paths
    }
    for entry in entries:
        raw_values = _entry_value_dict(entry).get("raw_values")
        if not isinstance(raw_values, dict):
            continue
        _collect_path_values(raw_values, paths, collected)
    return [separator.join(collected[path]) for path in paths]


def _collect_path_values(
    raw_values: Dict[str, Any],
    paths: List[Tuple[str, ...]],
    collected: Dict[Tuple[str, ...], List[str]],
) -> None:
    for path in paths:
        value = resolve_nested_value(raw_values, path)
        if is_empty_partner_value(value):
            continue
        collected[path].append(str(value))


def build_primitive_field_cell(
    entries: List[Dict[str, Any]],
    separator: str,
) -> str:
    '''
    Build a single joined cell for a primitive partner field by
    collecting each contribution's `raw_value` and skipping empties.
    '''
    values: List[str] = []
    for entry in entries:
        raw_value = _entry_value_dict(entry).get("raw_value")
        if is_empty_partner_value(raw_value):
            continue
        values.append(str(raw_value))
    return separator.join(values)
