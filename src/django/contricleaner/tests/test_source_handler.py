from django.contricleaner.lib.contri_cleaner_serializer import SourceHandler
from contricleaner.lib.source_parser import SourceParser
from contricleaner.lib.header_handler import HeaderHandler
from contricleaner.lib.header_dto import HeaderDTO
from contricleaner.lib.row_dto import RowDTO
import unittest
from unittest.mock import MagicMock


class SourceHandlerTest(unittest.TestCase):
    def setUp(self):
        self.source_parser = MagicMock(spec=SourceParser)
        self.header_handler = MagicMock(spec=HeaderHandler)
        self.source_handler = SourceHandler(self.source_parser, self.header_handler)

    def test_get_validated_header(self):
        raw_header = "Name, Age, Email"
        expected_header = HeaderDTO(["Name", "Age", "Email"])
        self.source_parser.get_raw_header.return_value = raw_header
        self.header_handler.get_validated_header.return_value = expected_header

        result = self.source_handler.get_validated_header()

        self.assertEqual(result, expected_header)
        self.source_parser.get_raw_header.assert_called_once()
        self.header_handler.get_validated_header.assert_called_once_with(raw_header)

    def test_get_validated_rows(self):
        expected_rows = [RowDTO(["John", "25", "john@example.com"]), RowDTO(["Jane", "30", "jane@example.com"])]
        self.assertEqual(self.source_handler.get_validated_rows(), expected_rows)
