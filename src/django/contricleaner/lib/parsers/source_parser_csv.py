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
        rows = []

        try:
            decoded_header = file.readline().decode(encoding='utf-8-sig') \
                .rstrip()
        except UnicodeDecodeError:
            raise ParsingError('Unsupported file encoding. Please '
                               'submit a UTF-8 CSV.')
        header = SourceParserCSV.__parse_csv_line(decoded_header)

        for idx, line in enumerate(file):
            if idx > 0:
                try:
                    decoded_row = line.decode(encoding='utf-8-sig').rstrip()
                except UnicodeDecodeError:
                    raise ParsingError('Unsupported file encoding. Please '
                                       'submit a UTF-8 CSV.')
                bare_row = SourceParserCSV.__parse_csv_line(decoded_row)
                rows.append(dict(zip(header, bare_row)))

        return rows

    @staticmethod
    def __parse_csv_line(line: str) -> list:
        return next(csv.reader([line]))
