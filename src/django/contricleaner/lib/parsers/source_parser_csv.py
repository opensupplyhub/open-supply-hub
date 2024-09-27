import csv
from typing import List

from django.db.models.fields.files import FieldFile

from contricleaner.lib.parsers.abstractions.source_parser import SourceParser
from contricleaner.lib.parsers.abstractions.file_parser import FileParser
from contricleaner.lib.exceptions.parsing_error import ParsingError


class SourceParserCSV(SourceParser, FileParser):
    def get_parsed_rows(self) -> List[dict]:
        return self._parse(self._file)

    @staticmethod
    def _parse(file: FieldFile) -> List[dict]:
        try:
            decoded_content = file.read().decode(encoding='utf-8-sig') \
                .splitlines()
        except UnicodeDecodeError:
            raise ParsingError('Unsupported file encoding. Please '
                               'submit a UTF-8 CSV.')

        rows = []
        header = SourceParserCSV.__parse_csv_line(decoded_content[0].rstrip())
        for line in decoded_content[1:]:
            bare_row = SourceParserCSV.__parse_csv_line(line.rstrip())
            rows.append(dict(zip(header, bare_row)))

        return rows

    @staticmethod
    def __parse_csv_line(line: str) -> list:
        return next(csv.reader([line]))
