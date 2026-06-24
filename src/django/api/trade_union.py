"""Helpers for stripping trade union-linked fields from API/download data.

Trade union-linked data is contributed by ``Contributor`` records whose
``contrib_type`` is ``Union``. For programmatic API access and bulk downloads
we hide every *field* a union contributed - extended fields (including the
union's own name/address entries), contributor-supplied partner fields and
sector - while keeping the facility itself and its canonical identity (the
resolved ``name``/``address``/``country_code``/``location`` columns on
``FacilityIndex``) fully visible. System or synthesized partner fields (e.g.
MIT living wage, wage indicator) are not union data and are never stripped
"""


def _contributor_id(entry):
    contributor = entry.get('contributor') or {}
    return contributor.get('id')


def strip_union_contributions(items, union_ids):
    if not union_ids or not items:
        return items

    return [
        item
        for item in items
        if _contributor_id(item) not in union_ids
    ]


def union_free_sector_values(facility, union_ids):
    """Return ``facility.sector`` values not solely contributed by a union.

    The flattened ``facility.sector`` array carries no attribution, so the
    union-only values are derived from the attributed ``item_sectors`` /
    ``claim_sectors`` arrays. A value is dropped only when every source that
    provided it is a trade union; values also supplied by another contributor
    or a claim are kept.
    """
    sector = getattr(facility, 'sector', None) or []
    if not union_ids or not sector:
        return sector

    union_values = set()
    other_values = set()

    for entry in (getattr(facility, 'item_sectors', None) or []):
        values = entry.get('sector') or []
        if _contributor_id(entry) in union_ids:
            union_values.update(values)
        else:
            other_values.update(values)

    for entry in (getattr(facility, 'claim_sectors', None) or []):
        other_values.update(entry.get('sector') or [])

    union_only_values = union_values - other_values
    if not union_only_values:
        return sector

    return [value for value in sector if value not in union_only_values]
