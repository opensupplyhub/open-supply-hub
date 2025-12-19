from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.partner_field import PartnerField
from api.models.us_county_tigerline import USCountyTigerline
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider


class MITLivingWageProviderTest(TestCase):
    def setUp(self):
        '''Set up test data for MIT living wage provider tests.'''
        self.email = 'test@example.com'
        self.user = User.objects.create(email=self.email)
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.CONTRIB_TYPE_CHOICES[0][0],
        )

        # Get or create mit_living_wage partner field.
        # Use get_all_including_inactive to access existing system field.
        try:
            self.partner_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name='mit_living_wage')
        except PartnerField.DoesNotExist:
            self.partner_field = PartnerField.objects.create(
                name='mit_living_wage',
                type=PartnerField.OBJECT,
                label='MIT Living Wage',
                system_field=True,
                active=True
            )

        # Clear all existing contributors and set only this contributor
        # to ensure test isolation from previous tests.
        self.partner_field.contributor_set.clear()
        self.contributor.partner_fields.add(self.partner_field)
        self.partner_field.refresh_from_db()

        # Delete all existing county data to ensure test isolation
        USCountyTigerline.objects.all().delete()

        # Create test county with geometry.
        # Use a test point in a remote location (middle of Pacific Ocean)
        # to avoid conflicts with real county data
        # Test point: lat: 0.0, lon: -150.0 (middle of Pacific)
        test_lat = 0.0
        test_lon = -150.0
        test_location = Point(test_lon, test_lat, srid=4326)

        # Transform point to EPSG:5070 and create a buffer around it
        point_5070 = test_location.transform(5070, clone=True)
        # Create a buffer of 50km (50000 meters) around the point
        # Buffer returns a Polygon, convert to MultiPolygon
        buffered_polygon = point_5070.buffer(50000)
        multipolygon = MultiPolygon(buffered_polygon, srid=5070)

        # Create test county data.
        self.county_data = USCountyTigerline.objects.create(
            geoid='99999',
            name='Test County',
            geometry=multipolygon
        )

        # Create test facility with location inside the test county.
        # Use Los Angeles coordinates (lat: 34.0522, lon: -118.2437)
        facility_list = FacilityList.objects.create(
            header='header',
            file_name='test',
            name='Test List'
        )

        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        # Create facility with location in EPSG:4326 (lat/lon)
        list_item = FacilityListItem.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            geocoded_point=test_location,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )

        self.facility = Facility.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code='US',
            location=test_location,
            created_from=list_item,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=list_item,
        )

        list_item.facility = self.facility
        list_item.save()

        self.provider = MITLivingWageProvider()

    def tearDown(self):
        '''Clean up test data but preserve system partner field.'''
        # Remove contributor assignments.
        self.partner_field.contributor_set.clear()
        # Clean up test county data.
        USCountyTigerline.objects.filter(geoid='99999').delete()
        # Note: We don't restore real county data as it would require
        # re-running the migration, which is expensive for tests

    def test_get_field_name(self):
        '''Test _get_field_name returns correct field name.'''
        field_name = self.provider._get_field_name()
        self.assertEqual(field_name, 'mit_living_wage')

    def test_fetch_raw_data_with_valid_location(self):
        '''Test _fetch_raw_data returns data for valid location.'''
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNotNone(raw_data)
        self.assertEqual(raw_data.geoid, '99999')
        self.assertEqual(raw_data.name, 'Test County')

    def test_fetch_raw_data_with_no_location(self):
        '''Test _fetch_raw_data returns None for facility without location.'''
        # Create a facility with all required fields
        facility_list = FacilityList.objects.create(
            header='header',
            file_name='test_no_location',
            name='Test List No Location'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Test Facility No Location',
            address='123 Test St',
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            geocoded_point=Point(0, 0, srid=4326),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility_no_location = Facility.objects.create(
            name='Test Facility No Location',
            address='123 Test St',
            country_code='US',
            location=Point(0, 0, srid=4326),  # Required for creation
            created_from=list_item,
        )
        # Manually set location to None in memory to test the method
        # (without saving to database, which would violate constraints)
        facility_no_location.location = None
        raw_data = self.provider._fetch_raw_data(facility_no_location)
        self.assertIsNone(raw_data)

    def test_fetch_raw_data_with_location_outside_county(self):
        '''Test _fetch_raw_data returns None for location outside county.'''
        # Use a location far from our test county
        # (e.g., different part of ocean)
        # Since we deleted all counties, this should return None
        ocean_location = Point(-100.0, 30.0, srid=4326)
        self.facility.location = ocean_location
        self.facility.save()
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNone(raw_data)

    def test_fetch_raw_data_with_invalid_country_code(self):
        '''Test _fetch_raw_data returns None for non-US territories.'''
        # Test with a non-US country code
        self.facility.country_code = 'GB'
        self.facility.save()
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNone(raw_data)

    def test_fetch_raw_data_with_valid_us_territories(self):
        '''Test _fetch_raw_data works for US, PR, and VI.'''
        # Test with US
        self.facility.country_code = 'US'
        self.facility.save()
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNotNone(raw_data)
        self.assertEqual(raw_data.geoid, '99999')

        # Test with Puerto Rico
        self.facility.country_code = 'PR'
        self.facility.save()
        raw_data = self.provider._fetch_raw_data(self.facility)
        # Should attempt lookup (may return None if no county found,
        # but shouldn't fail due to country code check)
        self.assertIsNotNone(raw_data)
        self.assertEqual(raw_data.geoid, '99999')

        # Test with US Virgin Islands
        self.facility.country_code = 'VI'
        self.facility.save()
        raw_data = self.provider._fetch_raw_data(self.facility)
        # Should attempt lookup
        self.assertIsNotNone(raw_data)
        self.assertEqual(raw_data.geoid, '99999')

    def test_format_data(self):
        '''Test _format_data formats MIT living wage data correctly.'''
        contributor_info = {
            'id': self.contributor.id,
            'name': self.contributor.name,
            'admin_id': self.contributor.admin_id,
            'is_verified': self.contributor.is_verified,
            'contrib_type': self.contributor.contrib_type,
        }

        formatted_data = self.provider._format_data(
            self.county_data,
            contributor_info
        )

        self.assertIsInstance(formatted_data, dict)
        self.assertEqual(formatted_data['field_name'], 'mit_living_wage')
        self.assertEqual(formatted_data['contributor'], contributor_info)
        self.assertIn('value', formatted_data)
        self.assertIn('raw_values', formatted_data['value'])

        raw_values = formatted_data['value']['raw_values']
        self.assertEqual(raw_values['value'], '99999')
        self.assertEqual(formatted_data['is_verified'], False)
        self.assertEqual(formatted_data['value_count'], 1)
        self.assertEqual(formatted_data['facility_list_item_id'], 1111)
        self.assertEqual(formatted_data['should_display_association'], True)

    def test_fetch_data_complete_flow(self):
        '''Test complete fetch_data flow returns formatted data.'''
        data = self.provider.fetch_data(self.facility)

        self.assertIsNotNone(data)
        self.assertEqual(data['field_name'], 'mit_living_wage')
        self.assertIn('contributor', data)
        self.assertEqual(data['contributor']['id'], self.contributor.id)
        self.assertIn('value', data)
        self.assertIn('raw_values', data['value'])
        self.assertEqual(data['value']['raw_values']['value'], '99999')

    def test_fetch_data_no_county_data(self):
        '''Test fetch_data returns None when no county data exists.'''
        # Delete the test county (all counties were deleted in setUp)
        self.county_data.delete()
        # Verify no counties exist
        self.assertEqual(USCountyTigerline.objects.count(), 0)
        data = self.provider.fetch_data(self.facility)
        self.assertIsNone(data)

    def test_fetch_data_no_contributor_assigned(self):
        '''Test fetch_data returns None when no contributor assigned.'''
        # Remove contributor from partner field.
        self.contributor.partner_fields.remove(self.partner_field)

        data = self.provider.fetch_data(self.facility)
        self.assertIsNone(data)

    def test_fetch_data_partner_field_inactive(self):
        '''Test fetch_data works when partner field is inactive.'''
        # Set the partner field to inactive.
        self.partner_field.active = False
        self.partner_field.save()

        # Should still work because provider uses get_all_including_inactive.
        data = self.provider.fetch_data(self.facility)
        self.assertIsNotNone(data)
