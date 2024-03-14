from typing import List
from abc import ABC, abstractmethod
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.sector_cache_interface import SectorCacheInterface
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.lib.parsers.source_parser import SourceParser


class ContriCleanerSerializer(ABC):
    '''
    TODO handle ['N/A', 'n/a', '?'] in utils.format_field
    that uses in FacilityIndexSerializer
    '''
    INVALID_KEYWORDS = ['N/A', 'n/a']

    def __init__(
            self,
            source_parser: SourceParser,
            sector_cache: SectorCacheInterface
    ):
        self.__source_parser = source_parser
        self.row_serializer = RowCompositeSerializer(sector_cache)

    @abstractmethod
    def clean_row(row: str) -> str:
        pass

    @staticmethod
    def _replace_invalid_data(value: str) -> str:
        result_value = value
        for keyword in ContriCleanerSerializer.INVALID_KEYWORDS:
            # Remove invalid keywords if exist.
            result_value = result_value.replace(keyword, '')
        return result_value

    def get_validated_rows(self) -> List[RowDTO]:
        rows = self.__source_parser.get_parsed_rows()
        return [self.row_serializer.get_validated_row(row) for row in rows]
