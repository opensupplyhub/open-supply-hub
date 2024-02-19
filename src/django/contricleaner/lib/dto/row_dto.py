from typing import NamedTuple


class RowDTO(NamedTuple):
    raw_json: any
    name: str
    clean_name: str
    address: str
    clean_address: str
    country_code: str
    sector: str

    fields: dict
    error: dict
