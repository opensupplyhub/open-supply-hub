from typing import List

from django.contricleaner.lib.parsers.data_parser import DataParser


class DataParserXLSX(DataParser):

    def __init__(self, data: dict):
        self.data = data

    def parsed_header(self) -> List[str]:
        return self.data.keys()

    def parsed_rows(self) -> List[dict]:
        return [self.data]
