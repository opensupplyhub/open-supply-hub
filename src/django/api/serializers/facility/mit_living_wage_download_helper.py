from typing import List, Optional

from api.models.partner_field import PartnerField
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider
from api.serializers.facility.partner_field_helper import (
    get_cached_all_partner_fields,
)


MIT_FIELD_NAME = MITLivingWageProvider.FIELD_NAME

COUNTY_LINK_HEADER = f'{MIT_FIELD_NAME}.county_link'
COUNTY_LINK_TEXT_HEADER = f'{MIT_FIELD_NAME}.county_link_text'

MIT_LIVING_WAGE_DOWNLOAD_HEADERS: List[str] = [
    COUNTY_LINK_HEADER,
    COUNTY_LINK_TEXT_HEADER,
]

EMPTY_CELLS: List[str] = ['', '']


class MITLivingWageDownloadHelper:
    '''
    Stateless helper that synthesizes the two download-only columns for
    `mit_living_wage` from the provider's raw_values + the partner
    field's configured `base_url` / `display_text`.
    '''

    def __init__(self) -> None:
        self.__provider = MITLivingWageProvider()
        self.__partner_field_resolved = False
        self.__partner_field: Optional[PartnerField] = None

    def get_cells(self, facility) -> List[str]:
        '''
        Return `[county_link, county_link_text]` for the given facility,
        or two empty strings if the provider has no data for it.
        '''
        try:
            data = self.__provider.fetch_data(facility)
        except Exception:
            return list(EMPTY_CELLS)
        if not isinstance(data, dict):
            return list(EMPTY_CELLS)

        raw_values = (data.get('value') or {}).get('raw_values') or {}
        county_id = raw_values.get('county_id')
        if not county_id:
            return list(EMPTY_CELLS)

        base_url, display_text = self.__resolve_display_config()
        county_link = (
            f'{base_url}{county_id}' if base_url else ''
        )
        return [county_link, display_text]

    def __resolve_display_config(self) -> tuple:
        '''
        Resolve (base_url, display_text) from the shared partner field
        cache, memoizing the lookup per instance. Falls back to empty
        strings if the partner field row is missing so a stale cache
        can't crash the download.
        '''
        if not self.__partner_field_resolved:
            self.__partner_field = next(
                (
                    pf
                    for pf in get_cached_all_partner_fields()
                    if pf.name == MIT_FIELD_NAME
                ),
                None,
            )
            self.__partner_field_resolved = True

        partner_field = self.__partner_field
        if partner_field is None:
            return '', ''
        return (
            partner_field.base_url or '',
            partner_field.display_text or '',
        )
