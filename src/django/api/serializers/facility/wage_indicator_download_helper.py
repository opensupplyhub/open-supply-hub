'''
Download-only transform for the `wage_indicator` system partner field.

Mirrors `mit_living_wage_download_helper` in spirit: it emits flat CSV/
XLSX columns at export time without touching the provider, the
`PartnerField` row, the `WageIndicatorCountryData` model, or running
any migration.

Unlike MIT — which stores only a `county_id` in `raw_values` and has to
concatenate it with `PartnerField.base_url` at render time — the
`WageIndicatorProvider` already emits both the URL and the display text
for every link directly in `raw_values` (see `get_links_with_text` on
`WageIndicatorCountryData`). So this helper is a pure projection: for
each of the three link types we emit one URL column and one text
column, in a fixed declaration order that matches
`WageIndicatorCountryData.LinkType`.

Cells are empty for any facility whose country has no
`WageIndicatorCountryData` row, for any environment where no
contributor is associated with the `wage_indicator` `PartnerField`
(the provider's `fetch_data` contract returns `None` in that case),
or for any individual link type the country's row leaves blank.
'''
from typing import List

from api.partner_fields.wage_indicator_provider import WageIndicatorProvider


WAGE_INDICATOR_FIELD_NAME = 'wage_indicator'

# The three link types the provider emits into `raw_values`, in the
# order `WageIndicatorCountryData.LinkType` declares them. Keeping this
# list as the single source of truth means adding/removing a link type
# on the model only requires updating `LinkType` and this list — the
# headers and row cells stay in lock-step automatically.
WAGE_INDICATOR_LINK_TYPES: List[str] = [
    'living_wage_link_national',
    'minimum_wage_link_english',
    'minimum_wage_link_national',
]


def _build_headers() -> List[str]:
    headers: List[str] = []
    for link_type in WAGE_INDICATOR_LINK_TYPES:
        headers.append(f'{WAGE_INDICATOR_FIELD_NAME}.{link_type}')
        headers.append(f'{WAGE_INDICATOR_FIELD_NAME}.{link_type}_text')
    return headers


WAGE_INDICATOR_DOWNLOAD_HEADERS: List[str] = _build_headers()

EMPTY_CELLS: List[str] = [''] * len(WAGE_INDICATOR_DOWNLOAD_HEADERS)


class WageIndicatorDownloadHelper:
    '''
    Stateless helper that projects `WageIndicatorProvider` output into
    six flat columns (URL + display text for each of the three link
    types). Instantiated once per serializer so the provider instance
    is reused across every row of a paginated download.
    '''

    def __init__(self) -> None:
        self.__provider = WageIndicatorProvider()

    def get_cells(self, facility) -> List[str]:
        '''
        Return the six ordered cells matching
        `WAGE_INDICATOR_DOWNLOAD_HEADERS`, or six empty strings if the
        provider has no data for this facility.
        '''
        try:
            data = self.__provider.fetch_data(facility)
        except Exception:
            return list(EMPTY_CELLS)
        if not isinstance(data, dict):
            return list(EMPTY_CELLS)

        raw_values = (data.get('value') or {}).get('raw_values') or {}
        if not isinstance(raw_values, dict):
            return list(EMPTY_CELLS)

        cells: List[str] = []
        for link_type in WAGE_INDICATOR_LINK_TYPES:
            cells.append(raw_values.get(link_type) or '')
            cells.append(raw_values.get(f'{link_type}_text') or '')
        return cells
