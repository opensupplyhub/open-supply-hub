import json
from typing import Any, Dict, Iterable, List, Optional, Set

from api.constants import MASKED_CONTRIBUTOR_LABEL
from api.helpers.data_center import (
    PROVENANCE_FIELDS,
    matched_values_include_data_center,
)
from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.services.masked_contributors import MaskedContributors

# OSDEV-3437: a single JSON-encoded column carrying every data-center-specific
# ExtendedField (OSDEV-2568) contributed for a facility. Unlike the partner
# field columns, this is not gated behind a PartnerField/system-field flag -
# it is always present in the header row, and populated only for facilities
# classified as a data center.
DATA_CENTER_INFORMATION_HEADER = 'data_center_information'

# OSDEV-3547: key, inside each row, holding the provenance of the
# FacilityListItem the row was contributed through.
PROVENANCE_KEY = 'provenance'

# The provenance schema's `added_on_date` is the FacilityListItem's
# `created_at` (see the OSDEV-3071 note on FacilityListItem).
ADDED_ON_DATE_KEY = 'added_on_date'

EMPTY_CELL = ''

UNKNOWN_CONTRIBUTOR_LABEL = '[Unknown Contributor]'


class DataCenterDownloadHelper:
    '''
    Helper that projects a facility's data-center-specific ExtendedField
    contributions into the single `data_center_information` download
    column: a JSON object keyed by contributor, each holding a list of
    "rows" - one dict of `{field_name: value}` per contribution (correlated
    by `facility_list_item_id`, so two different submissions from the same
    contributor never get merged into one row).

    Each row also carries a `provenance` object with the values stored on
    the FacilityListItem it was contributed through (OSDEV-3547). Rows
    without a `facility_list_item_id`, or whose item no longer exists, have
    no `provenance` key.

    Contributor identity follows the same masking rule `get_contributors`
    uses: a masked contributor's rows are still included (never dropped),
    just bucketed under the shared `MASKED_CONTRIBUTOR_LABEL` key instead
    of their real name, so every masked contributor's data-center rows
    collapse into one anonymous bucket.

    The data-center fields come from `facility.extended_fields` (already
    present on every download row). Provenance is not in the index, so it
    is read from `FacilityListItem` and cached on the helper. Call
    `prefetch_provenance` with a whole page of facilities to load it in one
    query; `get_cell` falls back to loading any items it is missing, so the
    output is correct either way and only the query count differs.
    '''

    def __init__(
        self, masked_contributors: Optional[MaskedContributors] = None
    ) -> None:
        self.__masked = masked_contributors or MaskedContributors()
        self.__provenance_by_item_id: Dict[int, Dict[str, Any]] = {}
        self.__loaded_item_ids: Set[int] = set()

    def prefetch_provenance(self, facilities: Iterable[Any]) -> None:
        '''
        Load, in a single query, the provenance of every FacilityListItem
        referenced by the data-center rows of `facilities`. Facilities that
        are not data centers are skipped, so a page without data centers
        makes no query.
        '''
        item_ids: Set[int] = set()
        for facility in facilities:
            extended_fields = getattr(facility, 'extended_fields', None) or []
            if self.__is_data_center(extended_fields):
                item_ids.update(self.__data_center_item_ids(extended_fields))

        self.__load_provenance(item_ids)

    def get_cell(self, facility) -> str:
        '''
        Return the JSON-encoded `data_center_information` cell for
        `facility`, or an empty string when the facility is not classified
        as a data center, or carries no data-center field values.
        '''
        extended_fields = getattr(facility, 'extended_fields', None) or []

        if not self.__is_data_center(extended_fields):
            return EMPTY_CELL

        rows_by_contributor = self.__group_by_contributor(extended_fields)
        if not rows_by_contributor:
            return EMPTY_CELL

        self.__load_provenance(
            {
                item_id
                for rows in rows_by_contributor.values()
                for item_id in rows
                if item_id is not None
            }
        )

        return json.dumps(
            {
                contributor_label: [
                    self.__with_provenance(row, item_id)
                    for item_id, row in rows.items()
                ]
                for contributor_label, rows in rows_by_contributor.items()
            },
            sort_keys=True,
        )

    @staticmethod
    def __is_data_center(extended_fields: List[Dict[str, Any]]) -> bool:
        '''
        A row is treated as a data center the same way `is_data_center`
        does for a live `Facility`: any `facility_type` ExtendedField value
        resolving to "Data Center". Checked against the already-loaded
        `extended_fields` payload instead of querying the database, since
        this runs once per row of a paginated bulk download.
        '''
        for entry in extended_fields:
            if not isinstance(entry, dict):
                continue
            if entry.get('field_name') != ExtendedField.FACILITY_TYPE:
                continue
            if matched_values_include_data_center(entry.get('value')):
                return True
        return False

    @staticmethod
    def __data_center_item_ids(
        extended_fields: List[Dict[str, Any]],
    ) -> Set[int]:
        '''
        Return the `facility_list_item_id`s of the data-center
        ExtendedFields on a facility.
        '''
        return {
            entry.get('facility_list_item_id')
            for entry in extended_fields
            if isinstance(entry, dict)
            and entry.get('field_name') in ExtendedField.DATA_CENTER_FIELDS
            and entry.get('facility_list_item_id') is not None
        }

    def __load_provenance(self, item_ids: Set[int]) -> None:
        '''
        Fetch the provenance of the FacilityListItems in `item_ids` that
        have not been loaded yet. Ids with no matching item are remembered
        too, so they are not queried again.
        '''
        missing_ids = item_ids - self.__loaded_item_ids
        if not missing_ids:
            return

        items = FacilityListItem.objects.filter(
            id__in=missing_ids
        ).values('id', 'created_at', *PROVENANCE_FIELDS)

        for item in items:
            created_at = item['created_at']
            provenance = {field: item[field] for field in PROVENANCE_FIELDS}
            provenance[ADDED_ON_DATE_KEY] = (
                created_at.date().isoformat() if created_at else None
            )
            self.__provenance_by_item_id[item['id']] = provenance

        self.__loaded_item_ids.update(missing_ids)

    def __with_provenance(
        self,
        row: Dict[str, Any],
        item_id: Any,
    ) -> Dict[str, Any]:
        '''
        Return `row` with the provenance of its FacilityListItem under
        `PROVENANCE_KEY`, or `row` unchanged when there is none.
        '''
        provenance = self.__provenance_by_item_id.get(item_id)
        if provenance is None:
            return row
        return {**row, PROVENANCE_KEY: provenance}

    def __contributor_label(self, contributor: Any) -> str:
        '''
        Return the display key for a contributor: `MASKED_CONTRIBUTOR_LABEL`
        when masked (mirroring `get_contributors`), its name when not, and
        a fallback label for a missing/malformed contributor blob.
        '''
        if not isinstance(contributor, dict) or not contributor:
            return UNKNOWN_CONTRIBUTOR_LABEL
        if self.__masked.should_mask(contributor):
            return MASKED_CONTRIBUTOR_LABEL
        return contributor.get('name') or UNKNOWN_CONTRIBUTOR_LABEL

    def __group_by_contributor(
        self,
        extended_fields: List[Dict[str, Any]],
    ) -> Dict[str, Dict[Any, Dict[str, Any]]]:
        '''
        Return `{contributor_label: {facility_list_item_id: {field_name:
        value, ...}}}` for every data-center ExtendedField
        (`ExtendedField.DATA_CENTER_FIELDS`) present on the facility.

        Fields are grouped into rows by `facility_list_item_id` so fields
        contributed together in one submission land in the same row, and
        two different submissions from the same contributor stay in
        separate rows rather than being interleaved. Entries with no
        `facility_list_item_id` (none exist on the current ingestion path,
        but nothing guarantees that stays true) fall back to one shared
        row per contributor, keyed by `None`, rather than being dropped.
        '''
        # Ordinary dicts (not defaultdict) so row order follows first
        # appearance, matching how `extended_fields` was assembled.
        rows_by_contributor: Dict[str, Dict[Any, Dict[str, Any]]] = {}

        for entry in extended_fields:
            if not isinstance(entry, dict):
                continue

            field_name = entry.get('field_name')
            if field_name not in ExtendedField.DATA_CENTER_FIELDS:
                continue

            value = entry.get('value')
            if not isinstance(value, dict):
                continue

            raw_value = value.get('raw_value')
            if raw_value in (None, '', []):
                continue

            contributor_label = self.__contributor_label(
                entry.get('contributor')
            )
            row_key = entry.get('facility_list_item_id')

            rows = rows_by_contributor.setdefault(contributor_label, {})
            row = rows.setdefault(row_key, {})

            self.__add_value_to_row(row, field_name, raw_value)

        return rows_by_contributor

    def __add_value_to_row(
        self,
        row: Dict[str, Any],
        field_name: str,
        value: Any
    ) -> None:
        '''
        Add a value to a row dict, merging with an existing value if
        present. If the existing value is a list, append to it; if not,
        convert it to a list and append the new value.
        '''
        if field_name in row:
            existing = row[field_name]
            if isinstance(existing, list):
                existing.append(value)
            else:
                row[field_name] = [existing, value]
        else:
            row[field_name] = value
