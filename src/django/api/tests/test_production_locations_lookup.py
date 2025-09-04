from django.test import TestCase
from django.contrib.gis.geos import Point

from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.models.facility.facility import Facility
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.services.production_locations_lookup import fetch_required_fields


class TestProductionLocationsLookup(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='t@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='contrib',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )
        self.facility_list = FacilityList.objects.create(
            header='header', file_name='name', name='list'
        )
        self.source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.facility_list,
            contributor=self.contributor
        )
        self.created_from_item = FacilityListItem.objects.create(
            name='Facility Base Name',
            address='Base Address',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            processing_results=[],
        )
        self.facility = Facility.objects.create(
            id='US123TESTID0001US',
            name='Facility Base Name',
            address='Base Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.created_from_item,
        )

    def test_returns_promoted_match_if_available(self):
        FacilityListItem.objects.create(
            name='Promoted Name',
            address='Promoted Address',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            facility=self.facility,
            processing_results=[{'action': 'promote_match'}],
        )
        results = fetch_required_fields(self.facility.id)
        self.assertEqual(results['name'], 'Promoted Name')
        self.assertEqual(results['address'], 'Promoted Address')
        self.assertEqual(results['country'], 'US')

    def test_returns_latest_list_item_if_no_promoted(self):
        FacilityListItem.objects.create(
            name='Older List Name',
            address='Older List Address',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            facility=self.facility,
            processing_results=[],
        )
        FacilityListItem.objects.create(
            name='Latest List Name',
            address='Latest List Address',
            country_code='US',
            sector=['Apparel'],
            row_index=2,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            facility=self.facility,
            processing_results=[],
        )
        results = fetch_required_fields(self.facility.id)
        self.assertEqual(results['name'], 'Latest List Name')
        self.assertEqual(results['address'], 'Latest List Address')
        self.assertEqual(results['country'], 'US')

    def test_falls_back_to_facility_if_no_list_items(self):
        results = fetch_required_fields(self.facility.id)
        self.assertEqual(results['name'], 'Facility Base Name')
        self.assertEqual(results['address'], 'Base Address')
        self.assertEqual(results['country'], 'US')
