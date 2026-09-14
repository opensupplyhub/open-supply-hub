import json
from typing import Any, Dict, List, Optional

from api.constants import MASKED_CONTRIBUTOR_LABEL
from api.helpers.data_center import matched_values_include_data_center
from api.models.extended_field import ExtendedField
from api.services.masked_contributors import MaskedContributors

# OSDEV-3437: a single JSON-encoded column carrying every data-center-specific
# ExtendedField (OSDEV-2568) contributed for a facility. Unlike the partner
# field columns, this is not gated behind a PartnerField/system-field flag -
# it is always present in the header row, and populated only for facilities
# classified as a data center.
DATA_CENTER_INFORMATION_HEADER = 'data_center_information'

EMPTY_CELL = ''

UNKNOWN_CONTRIBUTOR_LABEL = '[Unknown Contributor]'


class DataCenterDownloadHelper:
    '''
    Stateless helper that projects a facility's data-center-specific
    ExtendedField contributions into the single `data_center_information`
    download column: a JSON object keyed by contributor, each holding a
    list of "rows" - one dict of `{field_name: value}` per contribution
    (correlated by `facility_list_item_id`, so two different submissions
    from the same contributor never get merged into one row).

    Contributor identity follows the same masking rule `get_contributors`
    uses: a masked contributor's rows are still included (never dropped),
    just bucketed under the shared `MASKED_CONTRIBUTOR_LABEL` key instead
    of their real name, so every masked contributor's data-center rows
    collapse into one anonymous bucket.

    Unlike `WageIndicatorDownloadHelper` / `MITLivingWageDownloadHelper`,
    this reads only `facility.extended_fields` (already present on every
    download row) - no provider call or per-row DB query is needed. Row-
    level context that isn't in that JSON (the submitted address/name)
    is deliberately left out rather than resolved with an extra query.
    '''

    def __init__(
        self, masked_contributors: Optional[MaskedContributors] = None
    ) -> None:
        self.__masked = masked_contributors or MaskedContributors()

    def get_cell(self, facility) -> str:
        '''
        Return the JSON-encoded `data_center_information` cell for
        `facility`, or an empty string when the facility is not classified
        as a data center, or carries no data-center field values.
        '''
        extended_fields = getattr(facility, 'extended_fields', None) or []

        if not self.__is_data_center(extended_fields):
            return EMPTY_CELL

        grouped = self.__group_by_contributor(extended_fields)
        if not grouped:
            return EMPTY_CELL

        return json.dumps(grouped, sort_keys=True)

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
    ) -> Dict[str, List[Dict[str, Any]]]:
        '''
        Return `{contributor_label: [{field_name: value, ...}, ...]}` for
        every data-center ExtendedField (`ExtendedField.DATA_CENTER_FIELDS`)
        present on the facility.

        Fields are grouped into rows by `facility_list_item_id` so fields
        contributed together in one submission land in the same row, and
        two different submissions from the same contributor stay in
        separate rows rather than being interleaved. Entries with no
        `facility_list_item_id` (none exist on the current ingestion path,
        but nothing guarantees that stays true) fall back to one shared
        row per contributor rather than being dropped.
        '''
        # contributor_label -> { row_key -> {field_name: value} }, using an
        # ordinary dict (not defaultdict) so row order follows first
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

            if field_name in row:
                # Two ExtendedField rows for the same field in the same
                # submission is not a normal outcome of ingestion, but
                # keep both rather than silently dropping one.
                existing = row[field_name]
                if isinstance(existing, list):
                    existing.append(raw_value)
                else:
                    row[field_name] = [existing, raw_value]
            else:
                row[field_name] = raw_value

        return {
            contributor_label: list(rows.values())
            for contributor_label, rows in rows_by_contributor.items()
        }
