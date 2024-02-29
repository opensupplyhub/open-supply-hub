from typing import List

from contricleaner.lib.source_parser import SourceParser


class SourceParserCsv(SourceParser):
    def __init__(self):
        pass

    def parsed_header(self) -> List[str]:
        pass

    def parsed_rows(self) -> List[dict]:
        pass


# # List[dict] CSV and XLSX
# [
#     {
#         address: 'value',
#         name: 'name'
#     }, # facility list item
#     {
#         address: 'value',
#         name: 'name'
#     } # facility list item
# ]
