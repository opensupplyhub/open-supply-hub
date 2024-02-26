from typing import List
from contricleaner.lib.source_parser import SourceParser


class SourceParserJSON(SourceParser):

    def __init__(self, data: dict):
        self.data = data

    def parsed_header(self) -> List[str]:
        return self.data.keys()

    def parsed_rows(self) -> List[dict]:
        return [self.data]
