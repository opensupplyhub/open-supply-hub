from unittest.mock import Mock

from django.contrib.gis.geos import Point
from django.test import TestCase

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
    ExtendedField,
)
from api.models.facility.facility_activity_report import FacilityActivityReport
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.serializers import (
    FacilityIndexDetailsSerializer,
    get_contributor_name,
)
from api.serializers.facility.facility_activity_report_serializer import (
    FacilityActivityReportSerializer
)
from api.models.wage_indicator_country_data import WageIndicatorCountryData


class FacilityIndexDetailsSerializerTest(TestCase):
    def setUp(self):
        self.name_one = "name_one"
        self.name_two = "name_two"
        self.name_three = "name_three"
        self.address_one = "address_one"
        self.address_two = "address_two"
        self.address_three = "address_three"
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.email_three = "three@example.com"
        self.contrib_one_name = "contributor one"
        self.contrib_two_name = "contributor two"
        self.contrib_three_name = "contributor three"
        self.country_code = "US"
        self.list_one_name = "one"
        self.list_two_name = "two"
        self.list_three_name = "three"
        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)
        self.user_three = User.objects.create(email=self.email_three)

        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name=self.contrib_one_name,
            contrib_type=Contributor.CONTRIB_TYPE_CHOICES[0][0],
        )

        self.contrib_two = Contributor.objects.create(
            admin=self.user_two,
            name=self.contrib_two_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_three = Contributor.objects.create(
            admin=self.user_three,
            name=self.contrib_three_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
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

        self.list_two = FacilityList.objects.create(
            header="header", file_name="two", name=self.list_two_name
        )
        self.list_three = FacilityList.objects.create(
            header="header", file_name="three", name=self.list_three_name
        )

        self.source_two = Source.objects.create(
            facility_list=self.list_two,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_two,
        )
        self.source_three = Source.objects.create(
            facility_list=self.list_three,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_three,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name=self.name_two,
            address=self.address_two,
            country_code=self.country_code,
            sector=["Mining", "Metals"],
            row_index="2",
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
        )

        self.list_item_tree = FacilityListItem.objects.create(
            name=self.name_three,
            address=self.address_three,
            country_code=self.country_code,
            sector=["Mining", "Metals"],
            row_index="2",
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_three,
        )

        self.facility = Facility.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.second_facility = Facility.objects.create(
            name=self.name_two,
            address=self.address_two,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.list_item_two,
        )

        self.third_facility = Facility.objects.create(
            name=self.name_three,
            address=self.address_three,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.list_item_tree,
        )

        self.facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_one,
        )

        self.facility_match_two = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_two,
        )

        self.list_item_one.facility = self.facility
        self.list_item_one.save()

        self.list_item_two.facility = self.facility
        self.list_item_two.save()

        self.facility_claim = FacilityClaim.objects.create(
            contributor=self.contrib_one,
            facility=self.facility,
            contact_person=self.contrib_one_name,
            company_name="Test",
            website="http://example.com",
            facility_description="description",
            status=FacilityClaimStatuses.APPROVED,
        )

        self.partner_field_1 = PartnerField.objects.create(
            name='test_data_field',
            type=PartnerField.STRING,
            label='Test Data Field'
        )

        self.contrib_one.partner_fields.add(
            self.partner_field_1
        )

    def test_has_sector_data(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertIn("sector", data["properties"])
        self.assertIsNotNone(data["properties"]["sector"])
        self.assertNotEqual([], data["properties"]["sector"])
        self.assertIn("contributor_id", data["properties"]["sector"][0])
        self.assertIn("contributor_name", data["properties"]["sector"][0])
        self.assertIn("values", data["properties"]["sector"][0])
        self.assertIn("updated_at", data["properties"]["sector"][0])

    def test_sector_includes_approved_claim(self):
        FacilityClaim.objects.create(
            contributor=self.contrib_one,
            facility=self.facility,
            contact_person="test",
            sector=["Beauty"],
            status=FacilityClaimStatuses.APPROVED,
        )
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertEqual(["Beauty"], data["properties"]["sector"][0]["values"])

    def test_sector_excludes_unapproved_claim(self):
        FacilityClaim.objects.create(
            contributor=self.contrib_one,
            facility=self.facility,
            contact_person="test",
            sector=["Beauty"],
            status=FacilityClaimStatuses.DENIED,
        )
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertNotEqual(
            ["Beauty"], data["properties"]["sector"][0]["values"]
        )

    def test_sector_data_ordered_by_updated_desc(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertNotEqual([], data["properties"]["sector"])
        self.assertGreater(
            data["properties"]["sector"][0]["updated_at"],
            data["properties"]["sector"][1]["updated_at"],
        )
        self.assertEqual(
            self.contrib_two_name,
            data["properties"]["sector"][0]["contributor_name"],
        )
        self.assertEqual(
            self.contrib_one_name,
            data["properties"]["sector"][1]["contributor_name"],
        )
        self.assertEqual(
            self.list_item_two.sector,
            data["properties"]["sector"][0]["values"],
        )
        self.assertEqual(
            self.list_item_one.sector,
            data["properties"]["sector"][1]["values"],
        )

    def test_only_queries_latest_update_per_contributor(self):
        list_three = FacilityList.objects.create(
            header="header", file_name="one", name="Three"
        )

        source_three = Source.objects.create(
            facility_list=list_three,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_one,
        )

        list_item_three = FacilityListItem.objects.create(
            name="Three",
            address="Address",
            country_code="US",
            sector=["Agriculture"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            facility=self.facility,
            source=source_three,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=list_item_three,
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        # Should be at top of list since most recently updated
        self.assertEqual(
            list_item_three.sector, data["properties"]["sector"][0]["values"]
        )
        self.assertEqual(
            self.contrib_one_name,
            data["properties"]["sector"][0]["contributor_name"],
        )
        # Only 1 other sector element, for the other contributor
        self.assertEqual(2, len(data["properties"]["sector"]))
        self.assertEqual(
            self.contrib_two_name,
            data["properties"]["sector"][1]["contributor_name"],
        )

    def test_excludes_null_sectors_from_approved_claim(self):
        self.source_two.is_active = False
        self.source_two.save()

        FacilityClaim.objects.create(
            contributor=self.contrib_two,
            facility=self.facility,
            status=FacilityClaimStatuses.APPROVED,
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertEqual(2, len(data["properties"]["sector"]))
        self.assertEqual(
            get_contributor_name(self.contrib_two, False),
            data["properties"]["sector"][0]["contributor_name"],
        )
        self.assertEqual(
            self.contrib_one_name,
            data["properties"]["sector"][1]["contributor_name"],
        )

    def test_inactive_and_private_sources_serializes_anonymized_sectors(self):
        self.source_one.is_active = False
        self.source_one.save()

        self.source_two.is_public = False
        self.source_two.save()

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertEqual(2, len(data["properties"]["sector"]))
        self.assertEqual(
            get_contributor_name(self.contrib_two, False),
            data["properties"]["sector"][0]["contributor_name"],
        )
        self.assertIsNone(data["properties"]["sector"][0]["contributor_id"])
        self.assertEqual(
            get_contributor_name(self.contrib_one, False),
            data["properties"]["sector"][1]["contributor_name"],
        )
        self.assertIsNone(data["properties"]["sector"][1]["contributor_id"])

    def test_inactive_match_serializes_anonymized_sectors(self):
        self.facility_match_one.is_active = False
        self.facility_match_one.save()

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertEqual(2, len(data["properties"]["sector"]))
        self.assertEqual(
            self.contrib_two_name,
            data["properties"]["sector"][0]["contributor_name"],
        )
        self.assertIsNotNone(data["properties"]["sector"][0]["contributor_id"])
        self.assertEqual(
            get_contributor_name(self.contrib_one, False),
            data["properties"]["sector"][1]["contributor_name"],
        )
        self.assertIsNone(data["properties"]["sector"][1]["contributor_id"])

    def test_prioritizes_claim_address(self):
        self.facility_claim.facility_address = "134 Claim St"
        self.facility_claim.facility_location = Point(44, 55)
        self.facility_claim.save()

        self.facility.location = self.facility_claim.facility_location
        self.facility.save()

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data
        self.assertEqual(
            data["properties"]["address"], self.facility_claim.facility_address
        )
        other_addresses = data["properties"]["other_addresses"]
        self.assertEqual(len(other_addresses), 2)
        self.assertIn(self.facility.address, other_addresses)

    def test_get_other_names(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        serializer = FacilityIndexDetailsSerializer()
        expected_other_names = {self.name_two}
        actual_other_names = serializer.get_other_names(facility_index)
        self.assertEqual(expected_other_names, actual_other_names)

    def test_get_other_names_embed_mode_active(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        serializer = FacilityIndexDetailsSerializer(
            context={'request': Mock(query_params={'embed': '1'})}
        )
        expected_other_names = []
        actual_other_names = serializer.get_other_names(facility_index)
        self.assertEqual(expected_other_names, actual_other_names)

    def test_get_activity_reports(self):
        FacilityActivityReport.objects.create(
            id=1,
            facility=self.facility,
            reported_by_user=self.user_one,
            reported_by_contributor=self.contrib_one,
            reason_for_report="reason",
            closure_state=FacilityActivityReport.CLOSED,
            status=FacilityActivityReport.PENDING,
        )

        activity_reports_data = FacilityActivityReportSerializer(
            FacilityActivityReport.objects.get(id=1)
        ).data

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        facility_index.activity_reports_info.append(activity_reports_data)
        facility_index.save()

        serializer = FacilityIndexDetailsSerializer(facility_index)
        actual_activity_reports = serializer.get_activity_reports(
            facility_index
        )

        for key, value in actual_activity_reports[0].items():
            self.assertEqual(activity_reports_data.get(key), value)

    def test_is_claimed_returns_true(self):
        FacilityClaim.objects.create(
            contributor=self.contrib_one,
            facility=self.facility,
            contact_person="test",
            sector=["Beauty"],
            status=FacilityClaimStatuses.APPROVED,
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertEqual(
            True, data["properties"]["is_claimed"]
        )

    def test_is_claimed_returns_false(self):
        FacilityClaim.objects.create(
            contributor=self.contrib_two,
            facility=self.second_facility,
            contact_person="test",
            sector=["Beauty"],
            status=FacilityClaimStatuses.DENIED,
        )

        FacilityClaim.objects.create(
            contributor=self.contrib_three,
            facility=self.third_facility,
            contact_person="test",
            sector=["Apparel"],
            status=FacilityClaimStatuses.PENDING,
        )

        facility_index_one = FacilityIndex.objects.get(
            id=self.second_facility.id)
        facility_index_two = FacilityIndex.objects.get(
            id=self.third_facility.id)
        data_one = FacilityIndexDetailsSerializer(facility_index_one).data
        data_two = FacilityIndexDetailsSerializer(facility_index_two).data

        self.assertEqual(
            False, data_one["properties"]["is_claimed"]
        )
        self.assertEqual(
            False, data_two["properties"]["is_claimed"]
        )

    def test_partner_fields_returns_dict(self):

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data
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

        data = FacilityIndexDetailsSerializer(facility_index).data
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

        data = FacilityIndexDetailsSerializer(facility_index).data
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('source_by', test_data_field[0])
        self.assertEqual(
            test_data_field[0]['source_by'],
            None
        )

    def test_partner_fields_includes_unit(self):
        self.partner_field_1.unit = 'kg'
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('unit', test_data_field[0])
        self.assertEqual(test_data_field[0]['unit'], 'kg')

    def test_partner_fields_unit_is_none_when_not_set(self):
        self.partner_field_1.unit = ''
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('unit', test_data_field[0])
        self.assertEqual(test_data_field[0]['unit'], '')

    def test_partner_fields_includes_label(self):
        self.partner_field_1.label = 'Emissions Data'
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('label', test_data_field[0])
        self.assertEqual(test_data_field[0]['label'], 'Emissions Data')

    def test_partner_fields_label_is_empty_when_not_set(self):
        self.partner_field_1.label = ''
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('label', test_data_field[0])
        self.assertEqual(test_data_field[0]['label'], '')

    def test_partner_fields_includes_json_schema(self):
        self.partner_field_1.json_schema = {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'format': 'uri',
                },
            },
        }
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('json_schema', test_data_field[0])
        self.assertEqual(
            test_data_field[0]['json_schema'],
            {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'format': 'uri',
                    },
                },
            }
        )

    def test_partner_fields_json_schema_none(self):
        self.partner_field_1.json_schema = None
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

        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data["properties"]["partner_fields"]
        test_data_field = partner_fields['test_data_field']

        self.assertEqual(len(test_data_field), 1)
        self.assertIn('json_schema', test_data_field[0])
        self.assertIsNone(test_data_field[0]['json_schema'])

    def test_system_partner_fields_wage_indicator(self):
        '''Test system-generated wage indicator partner field in API.'''
        # Get or create wage_indicator partner field.
        try:
            wage_indicator_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name='wage_indicator')
        except PartnerField.DoesNotExist:
            wage_indicator_field = PartnerField.objects.create(
                name='wage_indicator',
                type=PartnerField.OBJECT,
                label='Wage Indicator',
                system_field=True,
                active=True
            )

        # Assign contributor to wage_indicator field.
        self.contrib_one.partner_fields.add(wage_indicator_field)

        # Get or create wage indicator data for US.
        WageIndicatorCountryData.objects.get_or_create(
            country_code='US',
            defaults={
                'living_wage_link_national': 'https://example.com/living',
                'minimum_wage_link_english': 'https://example.com/min-en',
                'minimum_wage_link_national': 'https://example.com/min-nat',
            }
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data['properties']['partner_fields']

        # Wage indicator should be present.
        self.assertIn('wage_indicator', partner_fields)

        wage_indicator_data = partner_fields['wage_indicator']
        self.assertIsInstance(wage_indicator_data, list)
        self.assertEqual(len(wage_indicator_data), 1)

        wage_indicator_item = wage_indicator_data[0]
        self.assertIn('contributor_id', wage_indicator_item)
        self.assertEqual(
            wage_indicator_item['contributor_id'],
            self.contrib_one.id
        )
        self.assertIn('contributor_name', wage_indicator_item)
        self.assertEqual(
            wage_indicator_item['contributor_name'],
            self.contrib_one.name
        )

        # Check value structure.
        self.assertIn('value', wage_indicator_item)
        self.assertIn('raw_values', wage_indicator_item['value'])

        raw_values = wage_indicator_item['value']['raw_values']
        # Data comes from actual wage indicator data, just check structure.
        self.assertIn('living_wage_link_national', raw_values)
        self.assertIn('minimum_wage_link_english', raw_values)
        self.assertIn('minimum_wage_link_national', raw_values)

    def test_system_partner_fields_no_contributor_assigned(self):
        '''Test system partner field returns nothing if no contributor.'''
        # Get or create wage_indicator partner field without assigning
        # contributor.
        try:
            wage_indicator_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name='wage_indicator')
            # Remove any existing contributors.
            wage_indicator_field.contributor_set.clear()
        except PartnerField.DoesNotExist:
            wage_indicator_field = PartnerField.objects.create(
                name='wage_indicator',
                type=PartnerField.OBJECT,
                label='Wage Indicator',
                system_field=True,
                active=True
            )

        # Get or create wage indicator data.
        WageIndicatorCountryData.objects.get_or_create(
            country_code='US',
            defaults={
                'living_wage_link_national': 'https://example.com/living',
            }
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data['properties']['partner_fields']

        # Wage indicator should not be present without contributor.
        self.assertNotIn('wage_indicator', partner_fields)

    def test_system_partner_fields_no_data_for_country(self):
        '''Test system partner field returns nothing if no data.'''
        # Get or create wage_indicator partner field.
        try:
            wage_indicator_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name='wage_indicator')
        except PartnerField.DoesNotExist:
            wage_indicator_field = PartnerField.objects.create(
                name='wage_indicator',
                type=PartnerField.OBJECT,
                label='Wage Indicator',
                system_field=True,
                active=True
            )

        # Assign contributor to wage_indicator field.
        self.contrib_one.partner_fields.add(wage_indicator_field)

        # Delete any wage indicator data for US to test empty state.
        WageIndicatorCountryData.objects.filter(country_code='US').delete()

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        data = FacilityIndexDetailsSerializer(facility_index).data
        partner_fields = data['properties']['partner_fields']

        # Wage indicator should not be present without data.
        self.assertNotIn('wage_indicator', partner_fields)
