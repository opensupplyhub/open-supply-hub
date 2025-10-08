from django.test import TestCase
from django.contrib.gis.geos import Point

from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.models.facility.facility import Facility
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.services.production_locations_lookup import (
    fetch_required_fields,
    has_coordinates,
    get_missing_required_fields,
    has_all_required_fields,
    has_some_required_fields,
    is_coordinates_without_all_required_fields,
)


class TestProductionLocationsLookup(TestCase):

    def setUp(self):
        self._create_test_user()
        self._create_test_contributor()
        self._create_test_facility_list()
        self._create_test_source()
        self._create_test_facility()

    def _create_test_user(self):
        self.user = User.objects.create(email='test@example.com')

    def _create_test_contributor(self):
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )

    def _create_test_facility_list(self):
        self.facility_list = FacilityList.objects.create(
            header='Test Header',
            file_name='test_file.csv',
            name='Test Facility List'
        )

    def _create_test_source(self):
        self.source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.facility_list,
            contributor=self.contributor
        )

    def _create_test_facility(self):
        self.created_from_item = FacilityListItem.objects.create(
            name='Base Facility Name',
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
            name='Base Facility Name',
            address='Base Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.created_from_item,
        )

    def _create_facility_list_item(self, **kwargs):
        defaults = {
            'name': 'Test Facility',
            'address': 'Test Address',
            'country_code': 'US',
            'sector': ['Apparel'],
            'row_index': 1,
            'status': FacilityListItem.CONFIRMED_MATCH,
            'source': self.source,
            'facility': self.facility,
            'processing_results': [],
        }
        defaults.update(kwargs)
        return FacilityListItem.objects.create(**defaults)

    def _assert_required_fields(
        self, result, expected_name, expected_address, expected_country
    ):
        self.assertEqual(result['name'], expected_name)
        self.assertEqual(result['address'], expected_address)
        self.assertEqual(result['country'], expected_country)

    def test_fetch_required_fields_returns_promoted_match_when_available(self):
        self._create_facility_list_item(
            name='Promoted Name',
            address='Promoted Address',
            country_code='US',
            processing_results=[{'action': 'promote_match'}],
        )

        result = fetch_required_fields(self.facility.id)
        self._assert_required_fields(
            result, 'Promoted Name', 'Promoted Address', 'US'
        )

    def test_fetch_required_fields_returns_latest_when_no_promoted_match(self):
        self._create_facility_list_item(
            name='Older Name',
            address='Older Address',
            country_code='US',
            row_index=1,
        )
        self._create_facility_list_item(
            name='Latest Name',
            address='Latest Address',
            country_code='US',
            row_index=2,
        )

        result = fetch_required_fields(self.facility.id)
        self._assert_required_fields(
            result, 'Latest Name', 'Latest Address', 'US'
        )

    def test_fetch_required_fields_falls_back_to_facility_when_no_items(self):
        result = fetch_required_fields(self.facility.id)
        self._assert_required_fields(
            result, 'Base Facility Name', 'Base Address', 'US'
        )

    def test_has_coordinates_with_coordinates_present(self):
        data = {'coordinates': {'lat': 40.7128, 'lng': -74.0060}}
        self.assertTrue(has_coordinates(data))

    def test_has_coordinates_without_coordinates(self):
        data = {'name': 'Test Facility'}
        self.assertFalse(has_coordinates(data))

    def test_get_missing_required_fields_with_all_fields_present(self):
        data = {'name': 'Test', 'address': '123 Main St', 'country': 'US'}
        self.assertEqual(get_missing_required_fields(data), [])

    def test_get_missing_required_fields_with_some_fields_missing(self):
        data = {'name': 'Test', 'address': '123 Main St'}
        self.assertEqual(get_missing_required_fields(data), ['country'])

    def test_get_missing_required_fields_with_all_fields_missing(self):
        data = {'other_field': 'value'}
        expected_fields = ['name', 'address', 'country']
        self.assertEqual(get_missing_required_fields(data), expected_fields)

    def test_has_all_required_fields_with_all_fields_present(self):
        data = {'name': 'Test', 'address': '123 Main St', 'country': 'US'}
        self.assertTrue(has_all_required_fields(data))

    def test_has_all_required_fields_with_missing_fields(self):
        data = {'name': 'Test', 'address': '123 Main St'}
        self.assertFalse(has_all_required_fields(data))

    def test_has_some_required_fields_with_some_fields_present(self):
        data = {'name': 'Test', 'address': '123 Main St'}
        self.assertTrue(has_some_required_fields(data))

    def test_has_some_required_fields_with_all_fields_present(self):
        data = {'name': 'Test', 'address': '123 Main St', 'country': 'US'}
        self.assertFalse(has_some_required_fields(data))

    def test_has_some_required_fields_with_no_fields_present(self):
        data = {'other_field': 'value'}
        self.assertFalse(has_some_required_fields(data))

    def test_is_coordinates_without_all_required_fields_coords_missing(self):
        data = {
            'coordinates': {'lat': 40.7128, 'lng': -74.0060},
            'name': 'Test',
            'address': '123 Main St'
        }
        self.assertTrue(is_coordinates_without_all_required_fields(data))

    def test_is_coordinates_without_all_required_fields_with_coords_all(self):
        data = {
            'coordinates': {'lat': 40.7128, 'lng': -74.0060},
            'name': 'Test',
            'address': '123 Main St',
            'country': 'US'
        }
        self.assertFalse(is_coordinates_without_all_required_fields(data))

    def test_is_coordinates_without_all_required_fields_without_coords(self):
        data = {'name': 'Test', 'address': '123 Main St'}
        self.assertFalse(is_coordinates_without_all_required_fields(data))
