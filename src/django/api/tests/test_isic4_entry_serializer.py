from django.test import SimpleTestCase

from api.serializers.v1.isic4_entry_serializer import ISIC4EntrySerializer
from api.serializers.v1.production_location_post_schema_serializer import (
    ProductionLocationPostSchemaSerializer,
)


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

    def test_missing_fields_are_allowed(self):
        serializer = ISIC4EntrySerializer(data={})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_blank_strings_are_rejected(self):
        invalid_payload = {
            **self.valid_payload,
            'section': '',
        }
        serializer = ISIC4EntrySerializer(data=invalid_payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('section', serializer.errors)


class ProductionLocationSchemaIsic4Test(SimpleTestCase):
    def setUp(self):
        self.valid_isic_entry = {
            'class': '620 - Computer programming, consultancy and related '
                     'activities',
            'group': '62 - Computer programming, consultancy and related '
                     'activities',
            'section': 'J - Information and communication',
            'division': '62 - Computer programming, consultancy and related '
                        'activities',
        }
        self.base_payload = {
            'name': 'Test Facility',
            'address': '123 Test Street',
            'country': 'US',
        }

    def test_multiple_isic_entries_allowed(self):
        payload = {
            **self.base_payload,
            'isic_4': [
                self.valid_isic_entry,
                self.valid_isic_entry,
            ],
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
