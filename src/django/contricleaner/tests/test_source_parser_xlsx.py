import os
from unittest.mock import MagicMock, patch

from defusedxml.common import EntitiesForbidden
from django.test import TestCase
from django.core.files.uploadedfile import (
    SimpleUploadedFile, TemporaryUploadedFile
)
from openpyxl import Workbook
from openpyxl.styles import NamedStyle

from contricleaner.lib.parsers.source_parser_xlsx import SourceParserXLSX
from contricleaner.lib.parsers.abstractions.source_parser import (
    SourceParser
)
from contricleaner.lib.parsers.abstractions.file_parser import (
    FileParser
)
from contricleaner.lib.serializers.row_serializers.row_composite_serializer \
    import RowCompositeSerializer
from contricleaner.lib.exceptions.parsing_error import ParsingError


class SourceParserXLSXTest(TestCase):
    def test_class_inherits_required_classes(self):
        temp_uploaded_file_stub = MagicMock(spec=TemporaryUploadedFile)
        source_parser_xlsx = SourceParserXLSX(temp_uploaded_file_stub)
        self.assertIsInstance(source_parser_xlsx, SourceParser)
        self.assertIsInstance(source_parser_xlsx, FileParser)

    def test_valid_xlsx_file_parsing(self):
        sheet_rows = (
            ('country', 'name', 'address', 'sector_product_type',
             'facility_type_processing_type', 'number_of_workers',
             'parent_company', 'percentage_of_male_workers'),
            ('United States', 'Fashion Plus',
             '123 Avenue Street,,,, Cityville,', 'Apparel|Jeans',
             'Embellishment', 1002, '', 2.00),
            ('Canada', 'N/A', '456 Main Road,,,, Townsville,',
             'n/a', 'Embossing', 1005, '', 3.50),
            ('Canada', 'Style Haven', '456 Fashion Road, Trendy Town',
             'Apparel|Jacket', '', 500, 'Style Super  ', 1),
            ('Italy', 'Chic Boutique', '789 Glamour Avenue,,,, Moda City,',
             'Apparel', 'Embossing', 3002, '', '20%')
        )

        expected_parsed_rows = [
            {
                'country': 'United States',
                'name': 'Fashion Plus',
                'address': '123 Avenue Street, Cityville',
                'sector_product_type': 'Apparel|Jeans',
                'facility_type_processing_type': 'Embellishment',
                'number_of_workers': '1002',
                'parent_company': '',
                'percentage_of_male_workers': '2%',
            },
            {
                'country': 'Canada',
                'name': '',
                'address': '456 Main Road, Townsville',
                'sector_product_type': '',
                'facility_type_processing_type': 'Embossing',
                'number_of_workers': '1005',
                'parent_company': '',
                'percentage_of_male_workers': '3.5%'
            },
            {
                'country': 'Canada',
                'name': 'Style Haven',
                'address': '456 Fashion Road, Trendy Town',
                'sector_product_type': 'Apparel|Jacket',
                'facility_type_processing_type': '',
                'number_of_workers': '500',
                'parent_company': 'Style Super',
                'percentage_of_male_workers': '100%'
            },
            {
                'country': 'Italy',
                'name': 'Chic Boutique',
                'address': '789 Glamour Avenue, Moda City',
                'sector_product_type': 'Apparel',
                'facility_type_processing_type': 'Embossing',
                'number_of_workers': '3002',
                'parent_company': '',
                'percentage_of_male_workers': '20%'
            },
        ]

        workbook = Workbook()
        sheet = workbook.active

        for row in sheet_rows:
            sheet.append(row)

        # Set number format for percentage and format to display as percentage
        # with 2 decimal places.
        percentage_style = NamedStyle(
            name='percentage',
            number_format='0.00%'
        )

        # Apply the percentage style to the column containing percentage
        # values (index 8)
        for row in sheet.iter_rows(min_row=1, max_row=len(sheet_rows),
                                   min_col=8, max_col=8):
            for cell in row:
                cell.style = percentage_style

        workbook.save('test.xlsx')

        with open('test.xlsx', 'rb') as xlsx_file:
            file_content = xlsx_file.read()
            uploaded_file = SimpleUploadedFile('test.xlsx', file_content)

        parser = SourceParserXLSX(uploaded_file)
        parsed_rows = parser.get_parsed_rows()
        parsed_rows = [RowCompositeSerializer.
                       clean_row(row) for row in parsed_rows]

        self.assertEqual(parsed_rows, expected_parsed_rows)

        os.remove('test.xlsx')

    @patch('contricleaner.lib.parsers.source_parser_xlsx.load_workbook')
    def test_entities_forbidden_exception(self, mock_load_workbook):
        mock_load_workbook.side_effect = EntitiesForbidden(
            name='', value='', base='', sysid='', pubid='', notation_name=''
        )
        temp_uploaded_file_stub = MagicMock(spec=TemporaryUploadedFile)
        parser = SourceParserXLSX(temp_uploaded_file_stub)

        with self.assertRaisesRegex(
                ParsingError,
                (r'Error parsing Excel \(\.xlsx\) file')
                ):
            parser.get_parsed_rows()
