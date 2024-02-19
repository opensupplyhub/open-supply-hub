from typing import List
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.dto.header_dto import HeaderDTO
from contricleaner.lib.dto.row_dto import RowDTO


class SourceHandler:
    def __init__(self, source: SourceParser):
        self.source = source
        pass

    def get_validated_header(self) -> HeaderDTO:
        return HeaderDTO(raw_header='', header=[])

    def get_validated_rows(self) -> List[RowDTO]:
        return []
