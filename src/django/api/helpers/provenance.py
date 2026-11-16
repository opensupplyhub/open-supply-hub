"""Per-row provenance of the FacilityListItem an ExtendedField came from.

Shared by the facility details endpoint (OSDEV-3073) and, opt-in through the
``detail_provenance_data`` query param, the facilities list endpoint
(OSDEV-3751). Provenance is not stored in the facility index, so it is read
from ``FacilityListItem`` in a single query per call.
"""
from typing import Any, Dict, Iterable, Set

from api.helpers.data_center import PROVENANCE_FIELDS
from api.models.facility.facility_list_item import FacilityListItem

# Key, inside a provenance object, holding the date the FacilityListItem was
# added (its `created_at`), matching the `data_center_information` download
# column (OSDEV-3547).
ADDED_ON_DATE_KEY = 'added_on_date'

# Serializer context key holding a prefetched
# `{facility_list_item_id: provenance}` map.
PROVENANCE_CONTEXT_KEY = 'provenance_by_list_item_id'

FACILITY_LIST_ITEM_ID_KEY = 'facility_list_item_id'

ProvenanceMap = Dict[int, Dict[str, Any]]


def collect_facility_list_item_ids(
    extended_fields: Iterable[Any],
) -> Set[int]:
    """Return the `facility_list_item_id`s referenced by extended-field
    entries, skipping malformed entries and entries with no list item
    (e.g. claim-born fields)."""
    return {
        entry.get(FACILITY_LIST_ITEM_ID_KEY)
        for entry in extended_fields
        if isinstance(entry, dict)
        and entry.get(FACILITY_LIST_ITEM_ID_KEY) is not None
    }


def build_extended_field_provenance_map(
    extended_fields: Iterable[Any],
) -> ProvenanceMap:
    """Bulk-load the provenance of the FacilityListItems referenced by
    `extended_fields`, in one query.

    Returns `{facility_list_item_id: provenance}`, where `provenance` holds
    the non-empty `PROVENANCE_FIELDS` values of the item plus its
    `added_on_date` (ISO date). Ids with no matching item are left out, so
    their entries serialize `provenance` as null. Makes no query when no
    entry references a list item.
    """
    item_ids = collect_facility_list_item_ids(extended_fields)
    if not item_ids:
        return {}

    provenance_map: ProvenanceMap = {}
    rows = FacilityListItem.objects.filter(
        id__in=item_ids
    ).values('id', 'created_at', *PROVENANCE_FIELDS)

    for row in rows:
        provenance = {
            field: row[field]
            for field in PROVENANCE_FIELDS
            if row[field] not in (None, '')
        }
        created_at = row['created_at']
        if created_at is not None:
            provenance[ADDED_ON_DATE_KEY] = created_at.date().isoformat()
        if provenance:
            provenance_map[row['id']] = provenance

    return provenance_map
