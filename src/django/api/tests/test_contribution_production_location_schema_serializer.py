from django.test import SimpleTestCase

from api.serializers.v1.production_location_post_schema_serializer import (
    ProductionLocationPostSchemaSerializer,
)


class ContributionProductionLocationSchemaSerializerTest(SimpleTestCase):
    def setUp(self):
        self.valid_isic_entry_1 = {
            'class': '620 - Computer programming, consultancy and related '
                     'activities',
            'group': '62 - Computer programming, consultancy and related '
                     'activities',
            'section': 'J - Information and communication',
            'division': '62 - Computer programming, consultancy and related '
                        'activities',
        }
        self.valid_isic_entry_2 = {
            'class': '561 - Restaurants and mobile food service activities',
            'group': '56 - Food and beverage service activities',
            'section': 'I - Accommodation and food service activities',
            'division': '56 - Food and beverage service activities',
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
                self.valid_isic_entry_1,
                self.valid_isic_entry_2,
            ],
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duplicate_isic_entries_are_rejected(self):
        '''Test that duplicate ISIC-4 objects in the array are rejected.'''
        payload = {
            **self.base_payload,
            'isic_4': [
                self.valid_isic_entry_1,
                self.valid_isic_entry_1,  # Duplicate.
            ],
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isic_4', serializer.errors)
        self.assertIn(
            'Duplicate ISIC-4 objects are not allowed',
            str(serializer.errors['isic_4'])
        )

    def test_duplicate_isic_entries_different_order_are_rejected(self):
        '''Test that duplicates are detected regardless of field order.'''
        entry_1 = {
            'class': '620',
            'group': '62',
            'section': 'J',
            'division': '62',
        }
        entry_2 = {
            'section': 'J',
            'division': '62',
            'class': '620',
            'group': '62',
        }
        payload = {
            **self.base_payload,
            'isic_4': [entry_1, entry_2],
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isic_4', serializer.errors)
        self.assertIn(
            'Duplicate ISIC-4 objects are not allowed',
            str(serializer.errors['isic_4'])
        )

    def test_empty_isic_object_rejected(self):
        '''Test that empty ISIC-4 objects are rejected.'''
        payload = {
            **self.base_payload,
            'isic_4': [{}],
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isic_4', serializer.errors)
        self.assertIn('cannot be empty', str(serializer.errors['isic_4']))

    def test_isic_dict_instead_of_list_rejected(self):
        '''Test that passing a dict instead of list for isic_4 is rejected.'''
        payload = {
            **self.base_payload,
            'isic_4': self.valid_isic_entry_1,  # Dict instead of list.
        }
        serializer = ProductionLocationPostSchemaSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isic_4', serializer.errors)
        self.assertIn(
            'must be a list',
            str(serializer.errors['isic_4'])
        )
