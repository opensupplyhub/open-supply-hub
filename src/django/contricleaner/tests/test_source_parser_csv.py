import csv
import os
from unittest.mock import MagicMock

from django.test import TestCase
from django.core.files.uploadedfile import (
    SimpleUploadedFile, TemporaryUploadedFile
)
from rest_framework.exceptions import ValidationError

from contricleaner.lib.parsers.source_parser_csv import SourceParserCSV
from django.contricleaner.lib.parsers.abstractions.source_parser import SourceParser
from django.contricleaner.lib.parsers.core_interfaces.file_parser import FileParser
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer


class SourceParserCSVTest(TestCase):
    def test_class_inherits_required_classes(self):
        temp_uploaded_file_stub = MagicMock(spec=TemporaryUploadedFile)
        source_parser_csv = SourceParserCSV(temp_uploaded_file_stub)
        self.assertIsInstance(source_parser_csv, SourceParser)
        self.assertIsInstance(source_parser_csv, FileParser)

    def test_valid_csv_file_parsing(self):
        expected_parsed_rows = [
            {
                'country': 'United States',
                'name': 'Fashion Plus',
                'address': '123 Avenue Street, Cityville',
                'sector_product_type': 'Apparel|Jeans',
                'facility_type_processing_type': 'Embellishment',
                'number_of_workers': '1002',
                'parent_company': '',
            },
            {
                'country': 'Canada',
                'name': 'Style Haven',
                'address': '456 Fashion Road, Trendy Town',
                'sector_product_type': 'Apparel|Jacket',
                'facility_type_processing_type': '',
                'number_of_workers': '70%',
                'parent_company': 'Style Super',
            },
            {
                'country': 'Italy',
                'name': 'Chic Boutique',
                'address': '789 Glamour Avenue, Moda City',
                'sector_product_type': 'Apparel',
                'facility_type_processing_type': 'Embossing',
                'number_of_workers': '3002',
                'parent_company': '',
            },
        ]

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

        parser = SourceParserCSV(uploaded_file)
        rows = parser.get_parsed_rows()
        rows = [RowCompositeSerializer.clean_row(row) for row in rows]

        self.assertEqual(rows, expected_parsed_rows)

        os.remove('test.csv')

    def test_header_utf8_encoding_validation(self):
        with open('test.csv', 'wb') as csv_file:
            csv_file.write(b'\xff\xfe')  # Non-UTF-8 data for the header.
        with open('test.csv', 'rb') as csv_file:
            file_content = csv_file.read()
            uploaded_file = SimpleUploadedFile('test.csv', file_content)

        parser = SourceParserCSV(uploaded_file)
        with self.assertRaisesRegex(ValidationError,
                                    (r'Unsupported file encoding\. '
                                     r'Please submit a UTF-8 CSV\.')):
            parser.get_parsed_rows()

        os.remove('test.csv')

    def test_row_utf8_encoding_validation(self):
        with open('test.csv', 'wb') as csv_file:
            csv_file.write(b'name\n')
            csv_file.write(b'\xff\xfe')  # Non-UTF-8 data for the row.
        with open('test.csv', 'rb') as csv_file:
            file_content = csv_file.read()
            uploaded_file = SimpleUploadedFile('test.csv', file_content)

        parser = SourceParserCSV(uploaded_file)
        with self.assertRaisesRegex(ValidationError,
                                    (r'Unsupported file encoding\. '
                                     r'Please submit a UTF-8 CSV\.')):
            parser.get_parsed_rows()

        os.remove('test.csv')
