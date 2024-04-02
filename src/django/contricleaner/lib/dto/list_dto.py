from typing import List, NamedTuple
from contricleaner.lib.dto.row_dto import RowDTO


class ListDTO(NamedTuple):
    rows: List[RowDTO]
    errors: List[dict]