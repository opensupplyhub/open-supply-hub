from contricleaner.lib.serializers.row_serializers.\
    row_facility_type_serializer import RowFacilityTypeSerializer

from django.test import TestCase


class RowFacilityTypeSerializerTest(TestCase):

    def setUp(self):
        self.split_pattern = r', |,|\|'
        self.serializer = RowFacilityTypeSerializer(self.split_pattern)

    def test_validate_with_no_values(self):
        row = {}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(validated, {})

    def test_validate_with_facility_type_processing_type(self):
        row = {'facility_type_processing_type':
               ['Blending|Knitting|Blending', 'Coating, Knitting']}
        current = {}
        validated = self.serializer.validate(row, current)

        self.assertEqual(
            validated['facility_type']['raw_values'],
            ['Blending|Knitting|Blending', 'Coating, Knitting']
        )

        # For 'processed_values', check that they contain the same values
        # (ignoring order).
        self.assertCountEqual(
            validated['facility_type']['processed_values'],
            ['Blending', 'Knitting', 'Coating']
        )

        self.assertEqual(
            validated['processing_type']['raw_values'],
            ['Blending|Knitting|Blending', 'Coating, Knitting']
        )

        # For 'processed_values', check that they contain the same values
        # (ignoring order).
        self.assertCountEqual(
            validated['processing_type']['processed_values'],
            ['Blending', 'Knitting', 'Coating']
        )

    def test_validate_with_processing_type_only(self):
        row = {'processing_type': 'Knitting'}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(
            validated,
            {
                'facility_type': {
                    'raw_values': 'Knitting',
                    'processed_values': ['Knitting'],
                },
                'processing_type': {
                    'raw_values': 'Knitting',
                    'processed_values': ['Knitting'],
                },
            },
        )

    def test_validate_with_facility_type_only(self):
        row = {'facility_type': 'Blending'}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(
            validated,
            {
                'facility_type': {
                    'raw_values': 'Blending',
                    'processed_values': ['Blending'],
                },
                'processing_type': {
                    'raw_values': 'Blending',
                    'processed_values': ['Blending'],
                },
            },
        )

    def test_validate_with_both_types_already_filled(self):
        row = {'facility_type': 'Blending', 'processing_type': 'Knitting'}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(
            validated,
            {
                'facility_type': {
                    'raw_values': 'Blending',
                    'processed_values': ['Blending'],
                },
                'processing_type': {
                    'raw_values': 'Knitting',
                    'processed_values': ['Knitting'],
                },
            },
        )

    def test_validate_with_invalid_facility_type(self):
        row = {'facility_type': 123}
        current = {'errors': []}
        validated = self.serializer.validate(row, current)
        self.assertEqual(
            validated,
            {
                'errors': [
                    {
                        'message': 'Expected value for facility_type to be a '
                        'string or a list of strings but got 123.',
                        'field': 'facility_type',
                        'type': 'ValueError',
                    },
                ],
            },
        )
