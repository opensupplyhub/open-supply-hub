from typing import List
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.dto.header_dto import HeaderDTO
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.header_validators.header_composite_validator import (
    HeaderCompositeValidator,
)
from contricleaner.lib.row_validators.row_composite_validator import (
    RowCompositeValidator
)


class SourceHandler:
    def __init__(self, source: SourceParser):
        self.source = source
        self.header_handler = HeaderCompositeValidator()
        self.row_validator = RowCompositeValidator()

    def get_validated_header(self) -> HeaderDTO:
        return self.header_handler \
            .get_validated_header(self.source.parsed_header())

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.source.parsed_rows()

        return [self.row_validator.get_validated_row(row) for row in rows]
