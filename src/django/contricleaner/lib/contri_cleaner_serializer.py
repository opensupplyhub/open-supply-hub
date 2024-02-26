from typing import List
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.dto.row_dto import RowDTO
from django.contricleaner.lib.row_validators.row_composite_serializer import (
    RowCompositeValidator
)


class ContriCleanerSerializer:
    def __init__(self, source: SourceParser):
        self.source = source
        self.row_validator = RowCompositeValidator()

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.source.parsed_rows()

        return [self.row_validator.get_validated_row(row) for row in rows]
