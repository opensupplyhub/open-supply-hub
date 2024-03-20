from django.test import TestCase

from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.parsers.source_parser_json import SourceParserJSON
from contricleaner.lib.serializers.contri_cleaner_serializer import (
    ContriCleanerSerializer,
)
from contricleaner.tests.mockSectorCache import MockSectorCache


class TestContriCleanerSerializer(TestCase):
    def setUp(self):
        self.json_data = {
            "country": "USA",
            "name": "Name of the company",
            "address": "1234 Main St",
        }
        self.split_pattern = r', |,|\|'

    def test_get_validated_rows_json_parser(self):
        # Test when a single valid row is returned
        serializer = ContriCleanerSerializer(
            SourceParserJSON(self.json_data),
            MockSectorCache(),
            self.split_pattern,
        )
        result = serializer.get_validated_rows()
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
