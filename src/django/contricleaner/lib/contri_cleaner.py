import os
from typing import Union

from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)

from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)
from contricleaner.lib.parsers.parsing_executor import (
    ParsingExecutor
)
from contricleaner.lib.parsers.source_parser_xlsx import (
    SourceParserXLSX
)
from contricleaner.lib.parsers.source_parser_csv import (
    SourceParserCSV
)
from contricleaner.lib.parsers.source_parser_json import SourceParserJSON
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.exceptions.parsing_error import ParsingError


class ContriCleaner:
    '''
    This is the facade for interacting with the ContriCleaner library.
    '''

    def __init__(self,
                 data: Union[
                     InMemoryUploadedFile, TemporaryUploadedFile, dict],
                 sector_cache: SectorCacheInterface) -> None:
        unsupported_data_value_type_message = ('The data value type should be '
                                               'either dict, '
                                               'InMemoryUploadedFile, or '
                                               'TemporaryUploadedFile.')
        unsupported_sector_cache_value_type_message = (
            'The sector_cache value type should be SectorCacheInterface.')
        assert isinstance(
            data,
            (dict, InMemoryUploadedFile, TemporaryUploadedFile)
        ), unsupported_data_value_type_message
        assert isinstance(
            sector_cache, SectorCacheInterface
        ), unsupported_sector_cache_value_type_message

        self.__data = data
        self.__sector_cache = sector_cache

    def process_data(self) -> ListDTO:
        parsing_executor = self.__define_parsing_strategy()
        validated_rows = parsing_executor.execute_parsing()

        return ListDTO(rows=validated_rows)

    def __define_parsing_strategy(self) -> ParsingExecutor:
        if isinstance(self.__data, dict):
            parsing_executor = ParsingExecutor(
                SourceParserJSON(self.__data), self.__sector_cache
            )
        else:
            ext = os.path.splitext(self.__data.name)[1].lower()
            if ext == '.xlsx':
                parsing_executor = ParsingExecutor(
                    SourceParserXLSX(self.__data),
                    self.__sector_cache
                )
            elif ext == '.csv':
                parsing_executor = ParsingExecutor(
                    SourceParserCSV(self.__data),
                    self.__sector_cache
                )
            else:
                raise ParsingError(
                    'Unsupported file type. Please '
                    'submit Excel or UTF-8 CSV.'
                )
        return parsing_executor
