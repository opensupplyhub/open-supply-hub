import os
import csv
from unittest.mock import MagicMock

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import File
from openpyxl import Workbook

from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.tests.sector_cache_mock import SectorCacheMock
from contricleaner.tests.os_id_cache_mock import OSIDCacheMock


class ContriCleanerTest(TestCase):

    def test_valid_xlsx_file_processing(self):
        sheet_rows = (
            (
                'country', 'name', 'address', 'sector_product_type',
                'facility_type_processing_type', 'number_of_workers',
                'parent_company'
            ),
            (
                'United States', 'Fashion Plus',
                '123 Avenue Street,,,, Cityville,', 'Apparel|Jeans',
                'Embellishment', 1002, ''
            )
        )

        expected_rows = [
            RowDTO(
                raw_json={
                    'country': 'United States',
                    'name': 'Fashion Plus',
                    'address': '123 Avenue Street,,,, Cityville,',
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
                    'facility_type_processing_type': 'Embellishment',
                    'sector_product_type': 'Apparel|Jeans',
                    'parent_company': '',
                    'number_of_workers': '1002',
                    'country': 'United States',
                },
                errors=[],
            )
        ]
        expected_result = ListDTO(
           rows=expected_rows
        )

        workbook = Workbook()
        sheet = workbook.active

        for sheet_row in sheet_rows:
            sheet.append(sheet_row)

        workbook.save('test.xlsx')

        with open('test.xlsx', 'rb') as xlsx_file:
            file_content = xlsx_file.read()
            uploaded_file = SimpleUploadedFile('test.xlsx', file_content)

        contri_cleaner = ContriCleaner(
            uploaded_file,
            SectorCacheMock(),
            OSIDCacheMock()
        )
        processed_list = contri_cleaner.process_data()

        self.assertEqual(len(processed_list.rows), len(expected_result.rows))
        self.assertEqual(processed_list, expected_result)

        os.remove('test.xlsx')

    def test_valid_csv_file_processing(self):
        expected_rows = [
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
                    'facility_type_processing_type': 'Embellishment',
                    'sector_product_type': 'Apparel|Jeans',
                    'country': 'United States',
                    'parent_company': '',
                    'number_of_workers': '1002',
                },
                errors=[],
            )
        ]
        expected_result = ListDTO(
            rows=expected_rows
        )

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
            ])

        with open('test.csv', 'rb') as csv_file:
            file_content = csv_file.read()
            uploaded_file = SimpleUploadedFile('test.csv', file_content)

        contri_cleaner = ContriCleaner(
            uploaded_file,
            SectorCacheMock(),
            OSIDCacheMock()
        )
        processed_list = contri_cleaner.process_data()

        self.assertEqual(len(processed_list.rows), len(expected_result.rows))
        self.assertEqual(processed_list, expected_result)

        os.remove('test.csv')

    def test_submit_unsupported_file_type_throws_exception(self):
        expected_error_message = (
            'We cannot accept the type of file you submitted. Please change '
            'your file to an Excel or UTF-8 CSV and reupload.'
        )
        expected_error_type = 'ParsingError'
        expected_error_field = 'non_field_errors'

        temp_uploaded_file_stub = MagicMock(spec=File)
        temp_uploaded_file_stub.name = 'mocked_file_name.txt'

        contri_cleaner = ContriCleaner(temp_uploaded_file_stub,
                                       SectorCacheMock(),
                                       OSIDCacheMock())
        contri_cleaner_processed_data = contri_cleaner.process_data()
        error_dict = contri_cleaner_processed_data.errors[0]
        error_message = error_dict['message']
        error_type = error_dict['type']
        error_field = error_dict['field']

        self.assertEqual(error_message, expected_error_message)
        self.assertEqual(error_type, expected_error_type)
        self.assertEqual(error_field, expected_error_field)

    def test_valid_json_processing(self):
        json_data = {
            'country': 'USA',
            'name': 'Name of the company',
            'address': '1234 Main St',
        }

        expected_rows = [
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
        expected_result = ListDTO(
            rows=expected_rows
        )

        contri_cleaner = ContriCleaner(
            json_data,
            SectorCacheMock(),
            OSIDCacheMock()
        )
        processed_list = contri_cleaner.process_data()

        self.assertEqual(len(processed_list.rows), len(expected_result.rows))
        self.assertEqual(processed_list, expected_result)
