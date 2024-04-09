from typing import List, NamedTuple, Dict

from contricleaner.lib.dto.row_dto import RowDTO


class ListDTO(NamedTuple):
    rows: List[RowDTO] = []
    errors: List[Dict] = []
