from django.test import TestCase
from django.contrib.gis.geos import Point
from django.core.cache import cache

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
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.models.wage_indicator_link_text_config import (
    WageIndicatorLinkTextConfig
)
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider


class WageIndicatorProviderTest(TestCase):
    def setUp(self):
        '''Set up test data for wage indicator provider tests.'''
        self.email = 'test@example.com'
        self.user = User.objects.create(email=self.email)
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.CONTRIB_TYPE_CHOICES[0][0],
        )

        # Get or create wage_indicator partner field.
        # Use get_all_including_inactive to access existing system field.
        try:
            self.partner_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name='wage_indicator')
        except PartnerField.DoesNotExist:
            self.partner_field = PartnerField.objects.create(
                name='wage_indicator',
                type=PartnerField.OBJECT,
                label='Wage Indicator',
                system_field=True,
                active=True
            )

        # Assign contributor to partner field.
        self.contributor.partner_fields.add(self.partner_field)

        # Create test production location with valid country code.
        self.test_country_code = 'GB'  # Use GB for testing.
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

        list_item = FacilityListItem.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code=self.test_country_code,
            sector=['Apparel'],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )

        self.facility = Facility.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code=self.test_country_code,
            location=Point(0, 0),
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

        # Clean up any existing wage data for test country.
        WageIndicatorCountryData.objects.filter(
            country_code=self.test_country_code
        ).delete()

        # Create wage indicator data for test country.
        self.wage_data = WageIndicatorCountryData.objects.create(
            country_code=self.test_country_code,
            living_wage_link_national='https://test.example.com/living',
            minimum_wage_link_english='https://test.example.com/min-en',
            minimum_wage_link_national='https://test.example.com/min-nat',
        )

        self.provider = WageIndicatorProvider()

    def tearDown(self):
        '''Clean up test data, but preserve system partner field.'''
        # Remove contributor assignments.
        self.partner_field.contributor_set.clear()
        # Clean up test wage data.
        WageIndicatorCountryData.objects.filter(
            country_code=self.test_country_code
        ).delete()

    def test_get_field_name(self):
        '''Test _get_field_name returns correct field name.'''
        field_name = self.provider._get_field_name()
        self.assertEqual(field_name, 'wage_indicator')

    def test_fetch_raw_data_with_valid_country(self):
        '''Test _fetch_raw_data returns data for valid country code.'''
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNotNone(raw_data)
        self.assertEqual(raw_data.country_code, self.test_country_code)
        self.assertEqual(
            raw_data.living_wage_link_national,
            'https://test.example.com/living'
        )

    def test_fetch_raw_data_with_invalid_country(self):
        '''Test _fetch_raw_data returns None for non-existent country.'''
        self.facility.country_code = 'ZZ'
        raw_data = self.provider._fetch_raw_data(self.facility)
        self.assertIsNone(raw_data)

    def test_format_data(self):
        '''Test _format_data formats wage indicator data correctly.'''
        contributor_info = {
            'id': self.contributor.id,
            'name': self.contributor.name,
            'admin_id': self.contributor.admin_id,
            'is_verified': self.contributor.is_verified,
            'contrib_type': self.contributor.contrib_type,
        }

        formatted_data = self.provider._format_data(
            self.wage_data,
            contributor_info
        )

        self.assertIsInstance(formatted_data, dict)
        self.assertEqual(formatted_data['field_name'], 'wage_indicator')
        self.assertEqual(formatted_data['contributor'], contributor_info)
        self.assertIn('value', formatted_data)
        self.assertIn('raw_values', formatted_data['value'])

        raw_values = formatted_data['value']['raw_values']
        self.assertEqual(
            raw_values['living_wage_link_national'],
            'https://test.example.com/living'
        )
        self.assertIn('living_wage_link_national_text', raw_values)

    def test_fetch_data_complete_flow(self):
        '''Test complete fetch_data flow returns formatted data.'''
        data = self.provider.fetch_data(self.facility)

        self.assertIsNotNone(data)
        self.assertEqual(data['field_name'], 'wage_indicator')
        self.assertIn('contributor', data)
        self.assertEqual(data['contributor']['id'], self.contributor.id)
        self.assertIn('value', data)

    def test_fetch_data_no_wage_data(self):
        '''Test fetch_data returns None when no wage data exists.'''
        self.facility.country_code = 'ZZ'
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

    def test_wage_indicator_link_text_config(self):
        '''
        Test WageIndicatorLinkTextConfig customizes display text for links.
        '''
        # Update existing or create link text config with custom text.
        custom_text = 'Custom Test Living Wage Text'
        WageIndicatorLinkTextConfig.objects \
            .update_or_create(
                link_type='living_wage_link_national',
                defaults={'display_text': custom_text}
            )

        # Clear cache to ensure new config is used.
        cache.delete('wage_indicator_link_texts')

        # Fetch data through provider.
        data = self.provider.fetch_data(self.facility)

        self.assertIsNotNone(data)
        raw_values = data['value']['raw_values']

        # Check that custom text is used.
        self.assertIn('living_wage_link_national_text', raw_values)
        self.assertEqual(
            raw_values['living_wage_link_national_text'],
            custom_text
        )

        # Verify link URL is still correct.
        self.assertEqual(
            raw_values['living_wage_link_national'],
            'https://test.example.com/living'
        )
