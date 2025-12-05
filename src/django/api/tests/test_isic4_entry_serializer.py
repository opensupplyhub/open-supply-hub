from django.test import SimpleTestCase

from api.serializers.v1.isic4_entry_serializer import ISIC4EntrySerializer


class ISIC4EntrySerializerTest(SimpleTestCase):
    def setUp(self):
        self.valid_payload = {
            'class': '620 - Computer programming, consultancy and related '
                     'activities',
            'group': '62 - Computer programming, consultancy and related '
                     'activities',
            'section': 'J - Information and communication',
            'division': '62 - Computer programming, consultancy and related '
                        'activities',
        }

    def test_valid_isic4_payload(self):
        serializer = ISIC4EntrySerializer(data=self.valid_payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data['group'],
            self.valid_payload['group'],
        )

    def test_missing_fields_are_not_allowed(self):
        serializer = ISIC4EntrySerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            (
                'ISIC-4 object cannot be empty. At least one field '
                '(section, division, group, or class) must be provided.'
            ),
            str(serializer.errors)
        )

    def test_blank_strings_are_rejected(self):
        invalid_payload = {
            **self.valid_payload,
            'section': '',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('section', serializer.errors)

    def test_blank_class_field_is_rejected(self):
        '''Test that blank string for 'class' field is rejected.'''
        invalid_payload = {
            **self.valid_payload,
            'class': '',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('class', serializer.errors)
        self.assertIn(
            'Field class must be a non-empty string',
            str(serializer.errors['class'])
        )

    def test_unknown_fields_are_rejected(self):
        '''
        Test that fields other than section, division, group, class
        are rejected.
        '''
        invalid_payload = {
            **self.valid_payload,
            'invalid_field': 'some value',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('invalid_field', serializer.errors)
        self.assertIn(
            'is not a valid ISIC-4 field',
            str(serializer.errors['invalid_field'])
        )

    def test_multiple_unknown_fields_are_rejected(self):
        '''Test that multiple unknown fields are all reported.'''
        invalid_payload = {
            'unknown_1': 'value1',
            'unknown_2': 'value2',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('unknown_1', serializer.errors)
        self.assertIn('unknown_2', serializer.errors)

    def test_numeric_values_are_rejected(self):
        '''Test that numeric values are rejected for ISIC-4 fields.'''
        invalid_payload = {
            **self.valid_payload,
            'class': 123,
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('class', serializer.errors)
        self.assertIn(
            'must be a string',
            str(serializer.errors['class'])
        )

    def test_numeric_values_for_multiple_fields_are_rejected(self):
        '''Test that numeric values in multiple fields are all rejected.'''
        invalid_payload = {
            'class': 123,
            'section': 456,
            'group': 'valid group',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('class', serializer.errors)
        self.assertIn('section', serializer.errors)
        self.assertNotIn('group', serializer.errors)

    def test_only_unknown_fields_shows_unknown_field_error(self):
        '''
        Test that when only unknown fields are present, unknown field
        error is shown (not empty error).
        '''
        invalid_payload = {
            'invalid_field': 'value',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('invalid_field', serializer.errors)
        # Should not show empty object error.
        self.assertNotIn('cannot be empty', str(serializer.errors))
