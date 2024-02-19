
from typing import List, NamedTuple, Set


class HeaderDTO(NamedTuple):
    raw_header: List[str]
    fields: Set[str]
    errors: List[dict]
    non_standard_fields: Set[str]


def header_errors(header: HeaderDTO):
    return [error for error in header.errors if error.get("type") == "Error"]
