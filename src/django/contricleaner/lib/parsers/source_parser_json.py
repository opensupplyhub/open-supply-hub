from typing import List

from contricleaner.lib.parsers.source_parser import SourceParser


class SourceParserJSON(SourceParser):

    def __init__(self, data: dict):
        self.data = data
        print('self.data', data)

    def get_parsed_header(self) -> List[str]:
        return list(self.data.keys())

    def get_parsed_rows(self) -> List[dict]:
        return [self.data]
