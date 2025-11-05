from api.models.partner_field import PartnerField
from api.models.facility.facility_index \
    import FacilityIndex
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
    ExtendedField,
)
from api.serializers.facility.facility_index_serializer \
    import FacilityIndexSerializer

from django.contrib.gis.geos import Point
from django.test import TestCase


class FacilityIndexSerializerTest(TestCase):
    def setUp(self):
        self.name_one = "name_one"
        self.address_one = "address_one"
        self.email_one = "one@example.com"
        self.contrib_one_name = "contributor one"
        self.country_code = "US"
        self.list_one_name = "one"

        self.user_one = User.objects.create(email=self.email_one)
        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name=self.contrib_one_name,
            contrib_type=Contributor.CONTRIB_TYPE_CHOICES[0][0],
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name=self.list_one_name
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_one,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
        )

        self.facility = Facility.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_one,
        )

        self.list_item_one.facility = self.facility
        self.list_item_one.save()

        self.partner_field_1 = PartnerField.objects.create(
            name='test_data_field',
            type=PartnerField.STRING,
            label='Test Data Field'
        )

        self.contrib_one.partner_fields.add(
            self.partner_field_1
        )

    def test_partner_fields_returns_dict(self):

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]

        self.assertIsInstance(
            partner_fields,
            dict
        )

    def test_partner_fields_exist(self):
        extended_field = ExtendedField.objects.create(
            facility=self.facility,
            field_name='test_data_field',
            value={'raw_value': 'Transport Data'},
            contributor=self.contrib_one
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)

        facility_index.extended_fields.append({
            'id': extended_field.id,
            'field_name': 'test_data_field',
            'value': {'raw_value': 'Transport Data'},
            'contributor': {
                'id': self.contrib_one.id,
                'name': self.contrib_one.name,
                'is_verified': self.contrib_one.is_verified,
            },
            'created_at': extended_field.created_at.isoformat(),
            'updated_at': extended_field.updated_at.isoformat(),
            'is_verified': False,
            'facility_list_item_id': None,
            'should_display_association': True,
            'value_count': 1,
        })

        facility_index.save()
        facility_index.refresh_from_db()

        data = FacilityIndexSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]

        test_data_field = partner_fields['test_data_field']

        self.assertIsInstance(test_data_field, list)
        self.assertEqual(len(test_data_field), 1)
        self.assertEqual(
            test_data_field[0]['value'],
            {'raw_value': 'Transport Data'}
        )

    def test_partner_fields_includes_source_by(self):
        self.partner_field_1.source_by = \
            '<strong>Climate TRACE</strong> source'
        self.partner_field_1.save()

        extended_field = ExtendedField.objects.create(
            facility=self.facility,
            field_name='test_data_field',
            value={'raw_value': 'Test Value'},
            contributor=self.contrib_one
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        facility_index.extended_fields.append({
            'id': extended_field.id,
            'field_name': 'test_data_field',
            'value': {'raw_value': 'Test Value'},
            'contributor': {
                'id': self.contrib_one.id,
                'name': self.contrib_one.name,
                'is_verified': self.contrib_one.is_verified,
            },
            'created_at': extended_field.created_at.isoformat(),
            'updated_at': extended_field.updated_at.isoformat(),
            'is_verified': False,
            'facility_list_item_id': None,
            'should_display_association': True,
            'value_count': 1,
        })
        facility_index.save()
        facility_index.refresh_from_db()

        data = FacilityIndexSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('source_by', test_data_field[0])
        self.assertEqual(
            test_data_field[0]['source_by'],
            '<strong>Climate TRACE</strong> source'
        )

    def test_partner_fields_source_by_is_none_when_not_set(self):
        extended_field = ExtendedField.objects.create(
            facility=self.facility,
            field_name='test_data_field',
            value={'raw_value': 'Test Value'},
            contributor=self.contrib_one
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        facility_index.extended_fields.append({
            'id': extended_field.id,
            'field_name': 'test_data_field',
            'value': {'raw_value': 'Test Value'},
            'contributor': {
                'id': self.contrib_one.id,
                'name': self.contrib_one.name,
                'is_verified': self.contrib_one.is_verified,
            },
            'created_at': extended_field.created_at.isoformat(),
            'updated_at': extended_field.updated_at.isoformat(),
            'is_verified': False,
            'facility_list_item_id': None,
            'should_display_association': True,
            'value_count': 1,
        })
        facility_index.save()
        facility_index.refresh_from_db()

        data = FacilityIndexSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('source_by', test_data_field[0])
        self.assertEqual(
            test_data_field[0]['source_by'],
            None
        )
