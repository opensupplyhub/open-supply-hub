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
    if filters in (None, {}):
        return {}
    if not isinstance(filters, dict):
        raise ValueError(
            'Filters must be a JSON object, e.g. '
            '{"sector": ["Textiles"]}.'
        )
    cleaned = {}
    for field, values in filters.items():
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
        items = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f'The "{field}" filter must list non-blank text '
                    'values.'
                )
            items.append(value.strip())
        if field == 'country':
            items = [item.upper() for item in items]
        elif field == 'product_type':
            items = list(dict.fromkeys(item.lower() for item in items))
        cleaned[field] = items
    return cleaned


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
    """
    if not filters:
        return None
    condition = Q()
    for field, values in clean_filters(filters).items():
        # AND across keys by default. See the FUTURE WORK note above
        # for more flexible combinations (OR between keys, groups).
        condition &= Q(**{FILTERABLE_FIELDS[field]: values})
    return condition
