from typing import List
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.dto.header_dto import HeaderDTO
from contricleaner.lib.dto.row_dto import RowDTO


class RowHandler:
    def __init__(self, header: HeaderDTO):
        self.header = header
        pass

    def get_validated_row(self, raw_row: dict) -> RowDTO:
        return RowDTO()


class SourceHandler:
    def __init__(self, source: SourceParser):
        self.source = source
        self.header_handler = HeaderHandler()
        pass

    def get_validated_header(self) -> HeaderDTO:
        return self.header_handler.get_validated_header(self.source.get_raw_header())

    def get_validated_rows(self) -> List[RowDTO]:
        return []
