from datetime import date, timedelta
from django.test import TestCase
from django.contrib.gis.geos import Point

from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.constants import FacilityClaimStatuses, JS_MAX_SAFE_INTEGER
from api.exceptions import BadRequestException
from api.serializers.facility.facility_create_claim_serializer import (
    FacilityCreateClaimSerializer,
)


class FacilityCreateClaimSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.user.set_password('password')
        self.user.save()

        self.contributor = Contributor.objects.create(
            name='Test Contributor', admin=self.user
        )

        self.facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='one'
        )

        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code='US',
            sector=['Apparel'],
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )

        self.facility = Facility.objects.create(
            name=self.list_item.name,
            address=self.list_item.address,
            country_code=self.list_item.country_code,
            location=Point(0, 0),
            created_from=self.list_item,
        )

    def test_valid_claim_with_all_emissions_fields(self):
        '''Test that claim with all valid emissions estimate fields is
        valid.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'opening_date': date(2020, 1, 1),
            'closing_date': date(2023, 12, 31),
            'estimated_annual_throughput': 100000,
            'energy_coal': 500000,
            'energy_natural_gas': 300000,
            'energy_diesel': 200000,
            'energy_kerosene': 150000,
            'energy_biomass': 100000,
            'energy_charcoal': 50000,
            'energy_animal_waste': 25000,
            'energy_electricity': 1000000,
            'energy_other': 75000,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['energy_coal'], 500000)
        self.assertEqual(
            serializer.validated_data['energy_natural_gas'], 300000
        )

    def test_opening_date_not_in_future(self):
        '''Test that opening_date cannot be in the future.'''
        future_date = date.today() + timedelta(days=1)
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            "opening_date": future_date,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('opening_date', serializer.errors)
        self.assertIn(
            'Please enter a valid date (not in the future)',
            str(serializer.errors['opening_date'])
        )

    def test_closing_date_not_in_future(self):
        '''Test that closing_date cannot be in the future.'''
        future_date = date.today() + timedelta(days=1)
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            "closing_date": future_date,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('closing_date', serializer.errors)
        self.assertIn(
            'Please enter a valid date (not in the future)',
            str(serializer.errors['closing_date'])
        )

    def test_opening_date_before_or_equal_closing_date(self):
        '''Test that opening_date must be before or equal to closing_date.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'opening_date': date(2020, 1, 1),
            'closing_date': date(2020, 1, 1),
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())

    def test_closing_date_before_opening_date_fails(self):
        '''Test that closing_date cannot be before opening_date.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            "opening_date": date(2020, 12, 31),
            "closing_date": date(2020, 1, 1),
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('opening_date', serializer.errors)
        self.assertIn('closing_date', serializer.errors)
        self.assertIn(
            'Opening date must be before or equal to closing date',
            str(serializer.errors['opening_date'])
        )

    def test_energy_fields_accept_valid_positive_integers(self):
        '''Test that all energy fields accept valid positive integers.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'energy_coal': 100,
            'energy_natural_gas': 200,
            'energy_diesel': 300,
            'energy_kerosene': 400,
            'energy_biomass': 500,
            'energy_charcoal': 600,
            'energy_animal_waste': 700,
            'energy_electricity': 800,
            'energy_other': 900,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())

    def test_energy_fields_reject_zero(self):
        '''Test that energy fields reject 0 (min_value=1).'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'energy_coal': 0,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('energy_coal', serializer.errors)
        self.assertIn(
            'greater than or equal to 1',
            str(serializer.errors['energy_coal'])
        )

    def test_energy_fields_reject_negative(self):
        '''Test that energy fields reject negative values.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'energy_natural_gas': -100,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('energy_natural_gas', serializer.errors)
        self.assertIn(
            'greater than or equal to 1',
            str(serializer.errors['energy_natural_gas'])
        )

    def test_energy_fields_respect_max_value(self):
        '''Test that energy fields cannot exceed JS_MAX_SAFE_INTEGER.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'energy_diesel': JS_MAX_SAFE_INTEGER + 1,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('energy_diesel', serializer.errors)
        self.assertIn(
            'less than or equal to',
            str(serializer.errors['energy_diesel'])
        )

    def test_energy_fields_optional(self):
        '''Test that energy fields are optional and can be omitted.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('energy_coal', serializer.validated_data)
        self.assertNotIn('energy_natural_gas', serializer.validated_data)

    def test_estimated_annual_throughput_valid_range(self):
        '''Test that estimated_annual_throughput accepts valid values.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'estimated_annual_throughput': 50000,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['estimated_annual_throughput'], 50000
        )

    def test_estimated_annual_throughput_rejects_zero(self):
        '''Test that estimated_annual_throughput rejects 0.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'estimated_annual_throughput': 0,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('estimated_annual_throughput', serializer.errors)

    def test_estimated_annual_throughput_optional(self):
        '''Test that estimated_annual_throughput is optional.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())
        self.assertNotIn(
            'estimated_annual_throughput', serializer.validated_data
        )

    def test_claim_with_existing_pending_claim_fails(self):
        '''
        Test that creating a claim on a facility with a pending claim
        fails.
        '''
        # Create an existing pending claim.
        FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            status=FacilityClaimStatuses.PENDING,
        )

        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )

        with self.assertRaises(BadRequestException) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            'There is already a pending claim on this facility',
            str(context.exception)
        )

    def test_claim_with_existing_approved_claim_fails(self):
        '''
        Test that creating a claim on a facility with an approved claim
        fails.
        '''
        # Create an existing approved claim.
        FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            status=FacilityClaimStatuses.APPROVED,
        )

        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )

        with self.assertRaises(BadRequestException) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            'There is already an approved claim on this facility',
            str(context.exception)
        )

    def test_dates_optional(self):
        '''Test that opening_date and closing_date are optional.'''
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://example.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/example',
            'estimated_annual_throughput': 100000,
            'energy_coal': 500000,
        }

        serializer = FacilityCreateClaimSerializer(
            data=data, context={'facility': self.facility}
        )
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('opening_date', serializer.validated_data)
        self.assertNotIn('closing_date', serializer.validated_data)
