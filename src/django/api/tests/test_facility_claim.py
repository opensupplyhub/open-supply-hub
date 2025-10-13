import json
from datetime import date

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
)
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.urls import reverse


class FacilityClaimTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor(name="Contributor", admin=self.user)
        self.contributor.save()

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name="list"
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="name",
            address="address",
            country_code="US",
            sector=["Apparel"],
            source=self.source_one,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )

        self.facility = Facility.objects.create(
            name="name",
            address="address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_one,
        )

    @override_switch("claim_a_facility", active=True)
    def test_requires_login(self):
        url = reverse("facility-claimed")
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_claimed_facilities_list(self):
        self.client.post(
            "/user-login/",
            {"email": self.email, "password": self.password},
            format="json",
        )
        url = reverse("facility-claimed")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual([], data)

        claim = FacilityClaim(
            facility=self.facility, contributor=self.contributor
        )
        claim.save()

        # A new claim should NOT appear in the claimed list
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual([], data)

        claim.status = FacilityClaimStatuses.APPROVED
        claim.save()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(1, len(data))

    @override_switch('claim_a_facility', active=True)
    def test_create_claim_with_emissions_estimate_fields(self):
        '''
        Test successfully creating a claim with all emissions estimate
        fields.
        '''
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

        claim_url = f'/api/facilities/{self.facility.id}/claim/'
        claim_data = {
            'your_name': 'John Doe',
            'your_title': 'Facility Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/facility',
            'opening_date': '2020-01-01',
            'closing_date': '2023-12-31',
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

        response = self.client.post(claim_url, claim_data)
        self.assertEqual(200, response.status_code)

        # Verify the claim was created.
        claim = FacilityClaim.objects.filter(facility=self.facility).first()
        self.assertIsNotNone(claim)
        self.assertEqual(claim.contact_person, 'John Doe')
        self.assertEqual(claim.job_title, 'Facility Manager')

    @override_switch('claim_a_facility', active=True)
    def test_create_claim_without_optional_emissions_fields(self):
        '''
        Test creating a claim without optional emissions estimate
        fields.
        '''
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

        claim_url = f'/api/facilities/{self.facility.id}/claim/'
        claim_data = {
            'your_name': 'Jane Smith',
            'your_title': 'Operations Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/facility',
        }

        response = self.client.post(claim_url, claim_data)
        self.assertEqual(200, response.status_code)

        # Verify the claim was created without emissions data.
        claim = FacilityClaim.objects.filter(facility=self.facility).first()
        self.assertIsNotNone(claim)
        self.assertIsNone(claim.opening_date)
        self.assertIsNone(claim.closing_date)
        self.assertIsNone(claim.estimated_annual_throughput)
        self.assertIsNone(claim.energy_coal)

    @override_switch('claim_a_facility', active=True)
    def test_create_claim_with_invalid_date_range(self):
        '''Test that creating a claim with invalid date range fails.'''
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

        claim_url = f'/api/facilities/{self.facility.id}/claim/'
        claim_data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/facility',
            'opening_date': '2023-12-31',
            'closing_date': '2020-01-01',
        }

        response = self.client.post(claim_url, claim_data)
        self.assertEqual(400, response.status_code)
        self.assertIn('opening_date', str(response.content))

    @override_switch('claim_a_facility', active=True)
    def test_create_claim_saves_energy_data_to_database(self):
        '''Test that energy data is correctly saved to the database.'''
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

        claim_url = f'/api/facilities/{self.facility.id}/claim/'
        claim_data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/facility',
            'opening_date': '2020-01-01',
            'closing_date': '2022-12-31',
            'estimated_annual_throughput': 50000,
            'energy_coal': 100000,
            'energy_natural_gas': 200000,
            'energy_diesel': 150000,
            'energy_kerosene': 50000,
            'energy_biomass': 75000,
            'energy_charcoal': 25000,
            'energy_animal_waste': 10000,
            'energy_electricity': 500000,
            'energy_other': 30000,
        }

        response = self.client.post(claim_url, claim_data)
        self.assertEqual(200, response.status_code)

        # Verify all fields are saved correctly.
        claim = FacilityClaim.objects.filter(facility=self.facility).first()
        self.assertIsNotNone(claim)
        self.assertEqual(claim.opening_date, date(2020, 1, 1))
        self.assertEqual(claim.closing_date, date(2022, 12, 31))
        self.assertEqual(claim.estimated_annual_throughput, 50000)
        self.assertEqual(claim.energy_coal, 100000)
        self.assertEqual(claim.energy_natural_gas, 200000)
        self.assertEqual(claim.energy_diesel, 150000)
        self.assertEqual(claim.energy_kerosene, 50000)
        self.assertEqual(claim.energy_biomass, 75000)
        self.assertEqual(claim.energy_charcoal, 25000)
        self.assertEqual(claim.energy_animal_waste, 10000)
        self.assertEqual(claim.energy_electricity, 500000)
        self.assertEqual(claim.energy_other, 30000)

    @override_switch('claim_a_facility', active=True)
    def test_create_claim_with_invalid_energy_value(self):
        '''Test that creating a claim with invalid energy values fails.'''
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

        claim_url = f'/api/facilities/{self.facility.id}/claim/'
        claim_data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile':
                'https://linkedin.com/company/facility',
            'energy_coal': 0,  # Should fail because min_value=1.
        }

        response = self.client.post(claim_url, claim_data)
        self.assertEqual(400, response.status_code)
        self.assertIn('energy_coal', str(response.content))
