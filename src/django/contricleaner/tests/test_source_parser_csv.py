import csv
import os
from unittest.mock import MagicMock

from django.test import TestCase
from django.core.files.uploadedfile import (
    SimpleUploadedFile
)
from django.core.files.base import File

from contricleaner.lib.parsers.source_parser_csv import SourceParserCSV
from contricleaner.lib.parsers.abstractions.source_parser import (
    SourceParser
)
from contricleaner.lib.parsers.abstractions.file_parser import (
    FileParser
)
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.tests.sector_cache_mock import SectorCacheMock


class SourceParserCSVTest(TestCase):
    def test_class_inherits_required_classes(self):
        temp_uploaded_file_stub = MagicMock(spec=File)
        source_parser_csv = SourceParserCSV(temp_uploaded_file_stub)
        self.assertIsInstance(source_parser_csv, SourceParser)
        self.assertIsInstance(source_parser_csv, FileParser)

    def test_valid_csv_file_parsing(self):
        expected_processed_rows = [
            RowDTO(
                raw_json={
                    'country': 'United States',
                    'name': 'Fashion Plus',
                    'address': '123 Avenue Street,,,, Cityville',
                    'sector_product_type': 'Apparel|Jeans',
                    'facility_type_processing_type': 'Embellishment',
                    'number_of_workers': '1002',
                    'parent_company': '',
                },
                name='Fashion Plus',
                clean_name='fashion plus',
                address='123 Avenue Street, Cityville',
                clean_address='123 avenue street cityville',
                country_code='US',
                sector=['Apparel'],
                fields={
                    'product_type': ['Jeans'],
                    'facility_type': {
                        'raw_values': 'Embellishment',
                        'processed_values': ['Embellishment'],
                    },
                    'processing_type': {
                        'raw_values': 'Embellishment',
                        'processed_values': ['Embellishment'],
                    },
                    'country': 'United States',
                    'parent_company': '',
                    'facility_type_processing_type': 'Embellishment',
                    'number_of_workers': '1002',
                    'sector_product_type': 'Apparel|Jeans',
                },
                errors=[],
            ),
            RowDTO(
                raw_json={
                    'country': 'Canada',
                    'name': 'Style Haven',
                    'address': '456 Fashion Road, Trendy Town',
                    'sector_product_type': 'Apparel|Jacket',
                    'facility_type_processing_type': '',
                    'number_of_workers': '70%',
                    'parent_company': 'Style Super',
                },
                name='Style Haven',
                clean_name='style haven',
                address='456 Fashion Road, Trendy Town',
                clean_address='456 fashion road trendy town',
                country_code='CA',
                sector=['Apparel'],
                fields={
                    'product_type': ['Jacket'],
                    'country': 'Canada',
                    'parent_company': 'Style Super',
                    'facility_type_processing_type': '',
                    'number_of_workers': '70%',
                    'sector_product_type': 'Apparel|Jacket',
                },
                errors=[],
            ),
            RowDTO(
                raw_json={
                    'country': 'Italy',
                    'name': 'Chic Boutique',
                    'address': '789 Glamour Avenue,,,, Moda City',
                    'sector_product_type': 'Apparel',
                    'facility_type_processing_type': 'Embossing',
                    'number_of_workers': '3002',
                    'parent_company': '',
                },
                name='Chic Boutique',
                clean_name='chic boutique',
                address='789 Glamour Avenue, Moda City',
                clean_address='789 glamour avenue moda city',
                country_code='IT',
                sector=['Apparel'],
                fields={
                    'facility_type': {
                        'raw_values': 'Embossing',
                        'processed_values': ['Embossing'],
                    },
                    'processing_type': {
                        'raw_values': 'Embossing',
                        'processed_values': ['Embossing'],
                    },
                    'country': 'Italy',
                    'parent_company': '',
                    'facility_type_processing_type': 'Embossing',
                    'number_of_workers': '3002',
                    'sector_product_type': 'Apparel',
                },
                errors=[],
            ),
        ]
        expected_processed_list = ListDTO(rows=expected_processed_rows)

        with open('test.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(('country', 'name', 'address',
                             'sector_product_type',
                             'facility_type_processing_type',
                             'number_of_workers', 'parent_company   '))
            writer.writerows([
                ('United States', 'Fashion Plus',
                    '123 Avenue Street,,,, Cityville', 'Apparel|Jeans',
                    'Embellishment', 1002, ''),
                ('Canada', 'Style Haven', '456 Fashion Road, Trendy Town',
                    'Apparel|Jacket', '', '70%', 'Style Super  '),
                ('Italy', 'Chic Boutique', '789 Glamour Avenue,,,, Moda City',
                 'Apparel', 'Embossing', 3002, '')
            ])

        with open('test.csv', 'rb') as csv_file:
            file_content = csv_file.read()
            uploaded_file = SimpleUploadedFile('test.csv', file_content)

        contri_cleaner = ContriCleaner(uploaded_file, SectorCacheMock())
        processed_list = contri_cleaner.process_data()

        self.assertEqual(processed_list.rows, expected_processed_list.rows)

        os.remove('test.csv')

    def test_file_utf8_encoding_validation(self):
        expected_error_message = (
            'Our system does not support the type of CSV file you submitted. '
            'Please save and export your file as a UTF-8 CSV or an Excel file '
            'and reupload.')
        expected_error_type = 'ParsingError'
        expected_error_field = 'non_field_errors'

        with open('test.csv', 'wb') as csv_file:
            csv_file.write(b'\xff\xfe')  # Non-UTF-8 data for the header.
        with open('test.csv', 'rb') as csv_file:
            file_content = csv_file.read()
            uploaded_file = SimpleUploadedFile('test.csv', file_content)

        contri_cleaner = ContriCleaner(uploaded_file, SectorCacheMock())
        processed_data = contri_cleaner.process_data()

        error_dict = processed_data.errors[0]
        error_message = error_dict['message']
        error_type = error_dict['type']
        error_field = error_dict['field']

        self.assertEqual(error_message, expected_error_message)
        self.assertEqual(error_type, expected_error_type)
        self.assertEqual(error_field, expected_error_field)

        os.remove('test.csv')
