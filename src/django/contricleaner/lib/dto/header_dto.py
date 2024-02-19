
from typing import List, NamedTuple


class HeaderDTO(NamedTuple):
    raw_header: str
    header: List[str]
    error: dict
