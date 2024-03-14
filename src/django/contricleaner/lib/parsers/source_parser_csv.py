import csv
from typing import List, Union

from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)

from contricleaner.lib.parsers.source_parser import SourceParser
from contricleaner.lib.parsers.file_parser import FileParser
from contricleaner.lib.serializers.contri_cleaner_serializer_csv \
    import ContriCleanerSerializerCsv


class SourceParserCSV(SourceParser, FileParser):
    def get_parsed_rows(self) -> List[dict]:
        return self._parse(self._file)

    @staticmethod
    def _parse(
            file: Union[InMemoryUploadedFile, TemporaryUploadedFile]
            ) -> List[dict]:
        rows = []

        try:
            decoded_header = file.readline().decode(encoding='utf-8-sig') \
                .rstrip()
        except UnicodeDecodeError:
            raise ValidationError('Unsupported file encoding. Please '
                                  'submit a UTF-8 CSV.')
        header = SourceParserCSV.__parse_csv_line(decoded_header)

        for idx, line in enumerate(file):
            if idx > 0:
                try:
                    decoded_row = line.decode(encoding='utf-8-sig').rstrip()
                except UnicodeDecodeError:
                    raise ValidationError('Unsupported file encoding. Please '
                                          'submit a UTF-8 CSV.')
                bare_row = SourceParserCSV.__parse_csv_line(decoded_row)
                cleaned_row = map(
                    ContriCleanerSerializerCsv._clean_row,
                    bare_row)
                rows.append(dict(zip(header, cleaned_row)))

        return rows

    @staticmethod
    def __parse_csv_line(line: str) -> list:
        return next(csv.reader([line]))
