from django.test import TestCase

from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.parsers.source_parser_json import SourceParserJSON
from contricleaner.lib.parsers.parsing_executor import (
    ParsingExecutor,
)
from contricleaner.tests.sector_cache_mock import SectorCacheMock


class TestParsingExecutor(TestCase):
    def setUp(self):
        self.json_data = {
            "country": "USA",
            "name": "Name of the company",
            "address": "1234 Main St",
        }

    def test_get_validated_rows_json_parser(self):
        # Test when a single valid row is returned
        parsing_executor = ParsingExecutor(
            SourceParserJSON(self.json_data),
            SectorCacheMock()
        )
        result = parsing_executor.execute_parsing()
        expected_result = [
            RowDTO(
                raw_json={
                    'country': 'USA',
                    'name': 'Name of the company',
                    'address': '1234 Main St',
                },
                name='Name of the company',
                clean_name='name of the company',
                address='1234 Main St',
                clean_address='1234 main st',
                country_code='US',
                sector=['Unspecified'],
                fields={'country': 'USA'},
                errors=[],
            )
        ]

        self.assertEqual(len(result), 1)
        self.assertEqual(result, expected_result)
