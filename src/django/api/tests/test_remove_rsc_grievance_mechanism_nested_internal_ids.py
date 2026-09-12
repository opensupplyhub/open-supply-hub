from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from api.models import Contributor, User
from api.models.extended_field import ExtendedField
from api.models.facility.facility import Facility
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.source import Source


class RemoveRscGrievanceMechanismNestedInternalIdsTest(TestCase):
    def setUp(self):
        user = User.objects.create(email='test@example.com')
        contributor = Contributor.objects.create(
            admin=user,
            name='Test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            name='Test list',
            file_name='test.csv',
            header='name,address,country',
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Test facility',
            address='Test address',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility = Facility.objects.create(
            id='US2026000TEST',
            name='Test facility',
            address='Test address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        list_item.facility = facility
        list_item.save()
        FacilityMatch.objects.create(
            facility=facility,
            facility_list_item=list_item,
            status=FacilityMatch.CONFIRMED,
            is_active=True,
            results={},
        )
        self.extended_field = ExtendedField.objects.create(
            contributor=contributor,
            facility=facility,
            facility_list_item=list_item,
            field_name='rsc_grievance_mechanism',
            value={
                'raw_values': {
                    'internal_ID': 'private-id',
                    'mechanism': 'Hotline',
                },
            },
        )
        self.facility = facility

    def test_bulk_update_trigger_refreshes_facility_index(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        indexed_field = next(
            field
            for field in facility_index.extended_fields
            if field['id'] == self.extended_field.id
        )
        self.assertIn('internal_ID', indexed_field['value']['raw_values'])

        call_command(
            'remove_rsc_grievance_mechanism_nested_internal_ids',
            '--batch-size',
            '1',
        )

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.extended_field.value,
            {'raw_values': {'mechanism': 'Hotline'}},
        )

        facility_index.refresh_from_db()
        indexed_field = next(
            field
            for field in facility_index.extended_fields
            if field['id'] == self.extended_field.id
        )
        self.assertEqual(
            indexed_field['value'],
            {'raw_values': {'mechanism': 'Hotline'}},
        )
