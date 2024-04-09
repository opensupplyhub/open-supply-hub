from django.test import TestCase

from contricleaner.lib.parsers.source_parser_json import SourceParserJSON
from contricleaner.lib.parsers.parsing_executor import (
    ParsingExecutor,
)


class TestParsingExecutor(TestCase):
    def setUp(self):
        self.json_data = {
            "country": "USA",
            "name": "Name of the company",
            "address": "1234 Main St",
        }

    def test_parsing_execution(self):
        # Test when a single valid row is returned
        parsing_executor = ParsingExecutor(
            SourceParserJSON(self.json_data)
        )
        result = parsing_executor.execute_parsing()
        expected_result = [{
            "country": "USA",
            "name": "Name of the company",
            "address": "1234 Main St",
        }]

        self.assertEqual(len(result), 1)
        self.assertEqual(result, expected_result)
