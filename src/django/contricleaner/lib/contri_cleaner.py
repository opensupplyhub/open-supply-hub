import os
from typing import Union, List, Dict

from django.core.files.base import File

from contricleaner.lib.client_abstractions.cache_interface import (
    CacheInterface
)
from api.os_id_cache import OSIDCache
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
from contricleaner.lib.handlers.list_row_handler import ListRowHandler
from contricleaner.lib.handlers.pre_validation_handler \
    import PreValidationHandler
from contricleaner.lib.handlers.serialization_handler \
    import SerializationHandler
from contricleaner.constants import NON_FIELD_ERRORS_KEY


class ContriCleaner:
    '''
    This is the facade for interacting with the ContriCleaner library.
    '''

    def __init__(self,
                 data: Union[File, Dict],
                 sector_cache: CacheInterface,
                 os_id_cache: CacheInterface) -> None:
        unsupported_data_value_type_message = ('The data value type should be '
                                               'either dict or File.')
        unsupported_sector_cache_value_type_message = (
            'The sector_cache value type should be CacheInterface.')
        assert isinstance(
            data,
            (dict, File)
        ), unsupported_data_value_type_message
        assert isinstance(
            sector_cache, CacheInterface
        ), unsupported_sector_cache_value_type_message

        self.__data = data
        self.__sector_cache = sector_cache
        self.__os_id_cache = os_id_cache

    def process_data(self) -> ListDTO:
        try:
            parsed_rows = self.__parse_data()
        except ParsingError as err:
            return ListDTO(errors=[{
                'message': str(err),
                'field': NON_FIELD_ERRORS_KEY,
                'type': 'ParsingError',
            }])

        entry_handler = self.__setup_handlers()

        processed_list = entry_handler.handle(parsed_rows)

        return processed_list

    def __parse_data(self) -> List[Dict]:
        parsing_executor = self.__define_parsing_strategy()
        parsed_rows = parsing_executor.execute_parsing()

        return parsed_rows

    def __define_parsing_strategy(self) -> ParsingExecutor:
        if isinstance(self.__data, dict):
            parsing_executor = ParsingExecutor(SourceParserJSON(self.__data))
        else:
            ext = os.path.splitext(self.__data.name)[1].lower()
            if ext == '.xlsx':
                parsing_executor = ParsingExecutor(
                    SourceParserXLSX(self.__data)
                )
            elif ext == '.csv':
                parsing_executor = ParsingExecutor(
                    SourceParserCSV(self.__data)
                )
            else:
                raise ParsingError(
                    'We cannot accept the type of file you submitted. Please '
                    'change your file to an Excel or UTF-8 CSV and reupload.'
                )
        return parsing_executor

    def __setup_handlers(self) -> ListRowHandler:
        handlers = (
            PreValidationHandler(),
            SerializationHandler(
                self.__sector_cache,
                self.__os_id_cache
            )
        )
        for index in range(len(handlers) - 1):
            handlers[index].set_next(handlers[index + 1])

        entry_handler = handlers[0]

        return entry_handler
