from typing import List

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from contricleaner.lib.parsers.source_parser import SourceParser
from contricleaner.lib.exceptions.validation_error import ValidationError


class SourceParserXLSX(SourceParser):
    def __init__(self, file):
        self.__file = file

    def get_parsed_rows(self) -> List[dict]:
        return self.__parse(self.__file)

    @staticmethod
    def __parse(file):
        try:
            ws = SourceParserXLSX.__get_xlsx_sheet(file)

            # openpyxl package is 1-indexed
            percent_col = [get_column_letter(cell.column)
                           for cell in ws[2] if '%' in cell.number_format]

            if percent_col:
                for col in percent_col:
                    for cell in ws[col]:
                        if cell.row != 1:
                            cell.value = SourceParserXLSX.__format_percent(
                                cell.value
                            )

            ws_rows = ws.rows
            # Using `next` will consome the row so that iteration of the data
            # rows will skipt the header row
            first_row = next(ws_rows)
            header = ','.join(
                [SourceParserXLSX.__format_cell_value(cell.value)
                 for cell in first_row])

            def format_row(row):
                return '"{}"'.format(
                    '","'.join([
                        SourceParserXLSX.__format_cell_value(cell.value)
                        for cell in row
                        ])
                    )

            rows = [format_row(row)
                    for row in ws_rows
                    if any(cell.value is not None for cell in row)]

            return header, rows
        except Exception:
            raise ValidationError('Error parsing Excel (.xlsx) file')

    @staticmethod
    def __get_xlsx_sheet(file):
        import defusedxml
        from defusedxml.common import EntitiesForbidden

        defusedxml.defuse_stdlib()

        try:
            wb = load_workbook(filename=file)
            ws = wb[wb.sheetnames[0]]

            return ws

        except EntitiesForbidden:
            raise ValidationError('This file may be damaged and '
                                  'cannot be processed safely')

    @staticmethod
    def __format_percent(value):
        if value is None or isinstance(value, str):
            return value
        if value <= 1.0:
            str_value = str(value * 100)
        else:
            str_value = str(value)
        if str_value[-2:] == '.0':
            str_value = str_value[0:len(str_value)-2]
        return str_value + '%'

    @staticmethod
    def __format_cell_value(value):
        if value is None:
            return ''
        return str(value)
