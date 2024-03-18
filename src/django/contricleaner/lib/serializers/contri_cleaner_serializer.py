from typing import List
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.sector_cache_interface import SectorCacheInterface
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.lib.parsers.source_parser import SourceParser


class ContriCleanerSerializer():
    def __init__(
        self,
        source_parser: SourceParser,
        sector_cache: SectorCacheInterface,
        sector_split_pattern: str,
    ):
        self.__source_parser = source_parser
        self.row_serializer = RowCompositeSerializer(
            sector_cache, sector_split_pattern
        )

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.__source_parser.get_parsed_rows()
        return [self.row_serializer.get_validated_row(row) for row in rows]
