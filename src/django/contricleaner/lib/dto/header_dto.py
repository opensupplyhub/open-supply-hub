from typing import List, NamedTuple


class HeaderDTO(NamedTuple):
    headers: List[str]
    errors: List[dict]
