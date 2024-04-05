from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.parsers.abstractions.source_parser import SourceParser


class ParsingExecutor:
    def __init__(
        self,
        source_parser: SourceParser,
    ):
        self.__source_parser = source_parser

    def execute_parsing(self) -> list[RowDTO]:
        return self.__source_parser.get_parsed_rows()
