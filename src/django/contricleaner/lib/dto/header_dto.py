
from typing import List, NamedTuple, Set


class HeaderDTO(NamedTuple):
    raw_header: List[str]
    fields: Set[str]
    errors: List[dict]
    non_standard_fields: Set[str]
