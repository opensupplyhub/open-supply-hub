from typing import List

from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.dto.header_dto import HeaderDTO
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from .header_serializers.header_composite_serializer \
    import HeaderCompositeSerializer
from contricleaner.lib.source_parser import SourceParser


class ContriCleanerSerializer:
    def __init__(self, source: SourceParser):
        self.source = source
        self.header_serializer = HeaderCompositeSerializer()
        self.row_serializer = RowCompositeSerializer()

    def get_validated_headers(self) -> HeaderDTO:
        headers = self.source.parsed_header()

        return self.header_serializer.get_validated_headers(headers)

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.source.parsed_rows()

        return [self.row_serializer.get_validated_row(row) for row in rows]
