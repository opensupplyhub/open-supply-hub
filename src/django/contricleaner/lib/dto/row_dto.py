from typing import List, NamedTuple


class RowDTO(NamedTuple):
    raw_fields: dict
    name: str
    clean_name: str
    address: str
    clean_address: str
    country_code: str
    sector: str

    fields: dict
    errors: List[dict]
