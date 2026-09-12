import json
from typing import Any, Dict, List

from api.helpers.data_center import matched_values_include_data_center
from api.models.extended_field import ExtendedField

# OSDEV-3437: a single JSON-encoded column carrying every data-center-specific
# ExtendedField (OSDEV-2568) contributed for a facility. Unlike the partner
# field columns, this is not gated behind a PartnerField/system-field flag -
# it is always present in the header row, and populated only for facilities
# classified as a data center.
DATA_CENTER_INFORMATION_HEADER = 'data_center_information'

EMPTY_CELL = ''


class DataCenterDownloadHelper:
    '''
    Stateless helper that projects a facility's data-center-specific
    ExtendedField contributions into the single `data_center_information`
    download column, as a JSON object keyed by field name.

    Unlike `WageIndicatorDownloadHelper` / `MITLivingWageDownloadHelper`,
    this reads only `facility.extended_fields` (already present on every
    download row) - no provider call or per-row DB query is needed.
    '''

    def get_cell(self, facility) -> str:
        '''
        Return the JSON-encoded `data_center_information` cell for
        `facility`, or an empty string when the facility is not classified
        as a data center, or carries no data-center field values.
        '''
        extended_fields = getattr(facility, 'extended_fields', None) or []

        if not self.__is_data_center(extended_fields):
            return EMPTY_CELL

        info = self.__collect_data_center_info(extended_fields)
        if not info:
            return EMPTY_CELL

        return json.dumps(info, sort_keys=True)

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
    def __collect_data_center_info(
        extended_fields: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        '''
        Return `{field_name: [value, ...]}` for every data-center
        ExtendedField (`ExtendedField.DATA_CENTER_FIELDS`) present on the
        facility.

        Every field is a list, even with a single contribution, so a
        facility carrying more than one contribution for the same field
        (e.g. from different list items or contributors) keeps all of
        them instead of the last one silently winning.
        '''
        info: Dict[str, Any] = {}

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

            if field_name in info:
                info[field_name].append(raw_value)
            else:
                info[field_name] = [raw_value]

        return info
