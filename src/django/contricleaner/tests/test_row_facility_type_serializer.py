from contricleaner.lib.serializers.row_serializers.\
    row_facility_type_serializer import RowFacilityTypeSerializer

from django.test import TestCase


class RowFacilityTypeSerializerTest(TestCase):

    def setUp(self):
        self.serializer = RowFacilityTypeSerializer()

    def test_validate_with_no_values(self):
        row = {}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(validated, {})

    def test_validate_with_facility_type_processing_type(self):
        row = {'facility_type_processing_type': 'Blending|Knitting'}
        current = {}
        validated = self.serializer.validate(row, current)
        self.assertEqual(
            validated,
            {
                'facility_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Blending', 'Knitting'},
                },
                'processing_type': {
                    'raw_values': 'Blending|Knitting',
                    'processed_values': {'Blending', 'Knitting'},
                },
            },
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
                    'processed_values': {'Knitting'},
                },
                'processing_type': {
                    'raw_values': 'Knitting',
                    'processed_values': {'Knitting'},
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
                    'processed_values': {'Blending'},
                },
                'processing_type': {
                    'raw_values': 'Blending',
                    'processed_values': {'Blending'},
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
                    'processed_values': {'Blending'},
                },
                'processing_type': {
                    'raw_values': 'Knitting',
                    'processed_values': {'Knitting'},
                },
            },
        )
