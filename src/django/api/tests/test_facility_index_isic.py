from django.db import connection

from api.models.extended_field import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilityIndexIsicTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        self.isic_field = ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.ISIC_4,
            value={
                'raw_value': [
                    {
                        'section': 'J - Information and communication',
                        'division': (
                            '62 - Computer programming, consultancy and '
                            'related activities'
                        ),
                        'group': '620 - Computer programming activities',
                        'class': '6201 - Computer programming activities',
                    },
                    {
                        'section': 'C - Manufacturing',
                        'class': (
                            '1410 - Manufacture of wearing apparel, '
                            'except fur apparel'
                        ),
                    },
                    {
                        'class': (
                            '0111 - Growing of cereals (except rice), '
                            'leguminous crops and oil seeds'
                        ),
                    },
                ],
            },
        )

    def _replace_entries(self, entries):
        self.isic_field.value = {'raw_value': entries}
        self.isic_field.save(update_fields=['value'])

    def _fetch_index_array(self, function_name, column_name):
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT array_agg({column_name}) FROM {function_name}(%s)',
                [self.facility.id],
            )
            row = cursor.fetchone()
        return sorted(row[0] or [])

    def test_index_isic_sql_functions_extract_normalized_codes(self):
        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['A', 'C', 'J'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['01', '14', '62'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            ['011', '141', '620'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_class', 'isic_class'),
            ['0111', '1410', '6201'],
        )

    def test_index_facilities_by_populates_isic_columns(self):
        with connection.cursor() as cursor:
            cursor.execute(
                'CALL index_facilities_by(%s)',
                [[self.facility.id]],
            )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(
            sorted(facility_index.isic_section),
            ['A', 'C', 'J'],
        )
        self.assertEqual(
            sorted(facility_index.isic_division),
            ['01', '14', '62'],
        )
        self.assertEqual(
            sorted(facility_index.isic_group),
            ['011', '141', '620'],
        )
        self.assertEqual(
            sorted(facility_index.isic_class),
            ['0111', '1410', '6201'],
        )

    def test_derives_ancestors_from_group_only(self):
        self._replace_entries([
            {'group': '011 - Growing of non-perennial crops'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['A'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['01'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            ['011'],
        )

    def test_derives_section_from_division_only(self):
        self._replace_entries([
            {'division': '62 - Computer programming activities'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['J'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['62'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            [],
        )

    def test_malformed_partial_codes_do_not_add_null_ancestors(self):
        self._replace_entries([
            {'group': '62 - Wrong length for an ISIC group'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            [],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            [],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            [],
        )

    def test_rev4_division_to_section_mapping_boundaries(self):
        expected_sections = {
            '01': 'A', '03': 'A',
            '05': 'B', '09': 'B',
            '10': 'C', '33': 'C',
            '35': 'D',
            '36': 'E', '39': 'E',
            '41': 'F', '43': 'F',
            '45': 'G', '47': 'G',
            '49': 'H', '53': 'H',
            '55': 'I', '56': 'I',
            '58': 'J', '63': 'J',
            '64': 'K', '66': 'K',
            '68': 'L',
            '69': 'M', '75': 'M',
            '77': 'N', '82': 'N',
            '84': 'O',
            '85': 'P',
            '86': 'Q', '88': 'Q',
            '90': 'R', '93': 'R',
            '94': 'S', '96': 'S',
            '97': 'T', '98': 'T',
            '99': 'U',
        }
        unmapped_codes = [
            '00', '04', '34', '40', '44', '48', '54', '57', '67',
            '76', '83', '89', '100', 'invalid', '',
        ]

        with connection.cursor() as cursor:
            for division_code, expected_section in expected_sections.items():
                with self.subTest(division_code=division_code):
                    cursor.execute(
                        'SELECT isic_rev4_section_for_division(%s)',
                        [division_code],
                    )
                    self.assertEqual(cursor.fetchone()[0], expected_section)

            for division_code in unmapped_codes:
                with self.subTest(division_code=division_code):
                    cursor.execute(
                        'SELECT isic_rev4_section_for_division(%s)',
                        [division_code],
                    )
                    self.assertIsNone(cursor.fetchone()[0])
