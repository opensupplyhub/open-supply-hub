from typing import List
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.row_serializers.row_composite_serializer import (
    RowCompositeSerializer,
)


class ContriCleanerSerializer:
    def __init__(self, source: SourceParser):
        self.source = source
        self.row_serializer = RowCompositeSerializer()

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.source.parsed_rows()

        return [self.row_serializer.get_validated_row(row) for row in rows]
