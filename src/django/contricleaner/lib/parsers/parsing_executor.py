from typing import List
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface)
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.lib.parsers.abstractions.source_parser import SourceParser


class ParsingExecutor:
    def __init__(
        self,
        source_parser: SourceParser,
        sector_cache: SectorCacheInterface,
    ):
        self.__source_parser = source_parser
        self.row_serializer = RowCompositeSerializer(sector_cache)

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.__source_parser.get_parsed_rows()
        return [self.row_serializer.get_validated_row(row) for row in rows]
