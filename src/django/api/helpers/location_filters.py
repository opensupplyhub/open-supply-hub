from typing import Any, Dict, Optional

from django.db.models import Q

# The fields a location filter may use, mapped to the FacilityIndex
# lookup that implements each one. Polygons (`Polygon.get_production_
# locations`) and zone sets share this one list, so a filter written
# for one means the same thing in the other. Two kinds of lookup
# appear because the underlying columns differ:
#   - `__in` fields hold ONE value per location (a location has
#     exactly one country), so the check is "is that value in the
#     requested list".
#   - `__overlap` fields are ARRAYS (a location can have several
#     sectors), so the check is "does the location's list share at
#     least one value with the requested list".
# To make a new field filterable, add an entry here — anything not in
# this allowlist is rejected with an error rather than silently
# ignored.
FILTERABLE_FIELDS = {
    'country': 'country_code__in',
    'sector': 'sector__overlap',
    'facility_type': 'facility_type__overlap',
    'processing_type': 'processing_type__overlap',
    'product_type': 'product_type__overlap',
    'parent_company': 'parent_company_name__overlap',
}

# The most values one key may list. Staff paste these by hand; a few hundred
# is already far more than any real dataset needs, and a limit keeps one
# mistaken paste from turning into an enormous query.
MAX_VALUES_PER_FILTER = 200


def has_filters(filters: Any) -> bool:
    """
    Whether a stored filter setting asks for any filtering.

    Only `None` and `{}` mean "no filters". Anything else, including an
    empty list or empty text that should never be stored, counts as a
    filter setting so that `clean_filters` can refuse it; treating such a
    value as "no filters" would quietly show a dataset on every location.
    """
    return filters is not None and filters != {}


def clean_filters(filters: Any) -> Dict[str, list]:
    """
    Validate a location-filter setting and return it in a normal form.

    A filter setting is a dict mapping an allowlisted field (see
    `FILTERABLE_FIELDS`) to the values a location must have, e.g.
    `{'sector': ['Textiles'], 'country': ['KH']}`. Within one key the
    values are OR'd; across keys the conditions are AND'd. A single
    string is accepted for a key and treated as a one-item list, and
    country codes are upper-cased so `'kh'` behaves like `'KH'`.

    Product types are lower-cased (and a repeat after lower-casing is
    dropped): the search index stores every product type in lower
    case (`index_product_type` lower-cases what contributors typed),
    so a filter value with capitals, such as `Sugar Cane`, could never
    match anything. Lower-casing here makes `Sugar Cane` and
    `sugar cane` the same filter. Sectors, facility types, processing
    types and parent companies are stored as typed, so they are left
    as they are and must match exactly.

    Anything that would quietly match nothing or everything is
    refused instead: an unknown key (a typo would otherwise filter
    nothing), an empty list (which matches no location, so the field
    would silently never show) and blank or non-string values.

    Args:
        filters: The setting as stored or typed. `None` and `{}` both
            mean "no filters".

    Returns:
        The normalized dict, `{}` for no filters.

    Raises:
        ValueError: With a message fit to show staff, when the setting
            is not usable.
    """
    if not has_filters(filters):
        return {}
    if not isinstance(filters, dict):
        raise ValueError(
            'Filters must be a JSON object, e.g. '
            '{"sector": ["Textiles"]}.'
        )
    return {
        field: _clean_field_values(field, values)
        for field, values in filters.items()
    }


def _clean_field_values(field: str, values: Any) -> list:
    """
    Validate and normalize the values of ONE filter key.

    Split out of `clean_filters` so each function stays small enough to
    read at a glance. The rules and messages are exactly those described
    in `clean_filters`.

    Args:
        field: The filter key, e.g. `sector`.
        values: The value or list of values given for it.

    Returns:
        The cleaned list of values for that key.

    Raises:
        ValueError: For an unknown key, an empty list, or a blank or
            non-text value.
    """
    if field not in FILTERABLE_FIELDS:
        raise ValueError(
            f'Unknown filter field "{field}". Allowed fields: '
            f'{", ".join(sorted(FILTERABLE_FIELDS))}.'
        )
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError(
            f'The "{field}" filter needs at least one value, e.g. '
            f'{{"{field}": ["..."]}}. An empty list would match no '
            'location.'
        )
    if len(values) > MAX_VALUES_PER_FILTER:
        raise ValueError(
            f'The "{field}" filter lists {len(values)} values; the limit '
            f'is {MAX_VALUES_PER_FILTER}.'
        )
    if any(not isinstance(value, str) or not value.strip()
           for value in values):
        raise ValueError(
            f'The "{field}" filter must list non-blank text values.'
        )
    return _normalize_values(field, [value.strip() for value in values])


def _normalize_values(field: str, items: list) -> list:
    """
    Apply the per-key normalization: country codes are upper-cased and
    product types are lower-cased with repeats dropped (the search index
    stores product types in lower case). Every other key is left as typed.
    """
    if field == 'country':
        return [item.upper() for item in items]
    if field == 'product_type':
        return list(dict.fromkeys(item.lower() for item in items))
    return items


def build_filters_q(filters: Optional[Dict[str, list]]) -> Optional[Q]:
    """
    Build the query condition for a (cleaned) location-filter setting,
    for a `FacilityIndex` queryset.

    How filters combine (the default, and today the only mode): the
    values inside one key are alternatives (OR, e.g. sector Mining or
    Agriculture), and the keys are combined with AND (e.g. a location
    must be in a chosen sector AND carry a listed product type).

    FUTURE WORK: this is deliberately simple. As more partners need
    filters we should make the system more flexible so that more
    complex rules can be applied: OR between different keys (sector X
    OR product Y), nested groups such as (A AND B) OR C, and NOT /
    exclusion rules. That likely means a richer stored format than
    this flat dict, plus an admin that can express it, so any change
    must keep this function, `clean_filters`, the zone set admin form
    and the search condition (`build_zone_sets_covered_q`) in step.

    Args:
        filters: A dict that `clean_filters` has accepted. Keys outside
            the allowlist raise `ValueError` here too, so a stored
            value that was never cleaned cannot widen a search.

    Returns:
        A `Q` AND-ing one lookup per key, or `None` when there are no
        filters (callers treat that as "no restriction", never as a
        condition to add).

    Raises:
        ValueError: When the setting is not usable (see `clean_filters`).
            Callers that serve data must not let this escape: see
            `ZoneSet.filters_condition`, which turns it into "match
            nothing".
    """
    if not has_filters(filters):
        return None
    condition = Q()
    for field, values in clean_filters(filters).items():
        # AND across keys by default. See the FUTURE WORK note above
        # for more flexible combinations (OR between keys, groups).
        condition &= Q(**{FILTERABLE_FIELDS[field]: values})
    return condition
