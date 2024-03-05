import csv
from typing import List

from contricleaner.lib.exceptions.validation_error import ValidationError
from contricleaner.lib.parsers.source_parser import SourceParser


class SourceParserCSV(SourceParser):
    def __init__(self, file):
        self.__file = file

    def get_parsed_rows(self) -> List[dict]:
        return self.__parse(self.__file)

    @staticmethod
    def __parse(file):
        rows = []

        try:
            header = SourceParserCSV.__parse_csv_line(
                file.readline().decode(encoding='utf-8-sig').rstrip()
            )
        except UnicodeDecodeError:
            raise ValidationError('Unsupported file encoding. Please '
                                  'submit a UTF-8 CSV.')

        for idx, line in enumerate(file):
            if idx > 0:
                try:
                    row = SourceParserCSV.__parse_csv_line(
                        line.decode(encoding='utf-8-sig').rstrip()
                    )
                    rows.append(dict(zip(header, row)))
                except UnicodeDecodeError:
                    raise ValidationError('Unsupported file encoding. Please '
                                          'submit a UTF-8 CSV.')

        return rows

    @staticmethod
    def __parse_csv_line(line):
        return list(csv.reader([line]))[0]
