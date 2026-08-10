from django.db import connection

from api.models.extended_field import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilityIndexIsicTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        ExtendedField.objects.create(
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
                            '0111 - Growing of cereals (except rice), '
                            'leguminous crops and oil seeds'
                        ),
                    },
                ],
            },
        )

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
            ['C', 'J'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['62'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            ['620'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_class', 'isic_class'),
            ['0111', '6201'],
        )

    def test_index_facilities_by_populates_isic_columns(self):
        with connection.cursor() as cursor:
            cursor.execute(
                'CALL index_facilities_by(%s)',
                [[self.facility.id]],
            )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(sorted(facility_index.isic_section), ['C', 'J'])
        self.assertEqual(facility_index.isic_division, ['62'])
        self.assertEqual(facility_index.isic_group, ['620'])
        self.assertEqual(sorted(facility_index.isic_class), ['0111', '6201'])
