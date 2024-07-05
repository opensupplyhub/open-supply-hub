import json

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

        self.claim_data = {
            'your_name': 'Test Name',
            'your_title': 'Test Title',
            'your_business_website': 'www.test.com',
            'business_website': 'www.test.com',
            'business_linkedin_profile': 'www.linkedin.com',
            'sectors': 'Apparel',
            'local_language_name': 'Local name',
        }

    def __login(self):
        self.client.login(email=self.email, password=self.password)

    @override_switch("claim_a_facility", active=True)
    def test_requires___login(self):
        url = reverse("facility-claimed")
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_claimed_facilities_list(self):
        self.__login()
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

        claim.status = FacilityClaim.APPROVED
        claim.save()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(1, len(data))

    @override_switch("claim_a_facility", active=True)
    def test_facility_claim_success(self):
        self.__login()
        url = "/api/facilities/{}/claim/".format(self.facility.id)

        response = self.client.post(url, self.claim_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FacilityClaim.objects.count(), 1)

    @override_switch("claim_a_facility", active=True)
    def test_facility_claim_with_valid_number_of_workers(self):
        self.__login()
        self.claim_data['number_of_workers'] = '2-251'

        url = "/api/facilities/{}/claim/".format(self.facility.id)

        response = self.client.post(url, self.claim_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FacilityClaim.objects.count(), 1)
        self.assertEqual(
            FacilityClaim.objects.first().facility_workers_count, '2-251'
        )

    @override_switch("claim_a_facility", active=True)
    def test_facility_claim_with_invalid_number_of_workers(self):
        self.__login()
        self.claim_data['number_of_workers'] = 'invalid'

        url = "/api/facilities/{}/claim/".format(self.facility.id)

        response = self.client.post(url, self.claim_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FacilityClaim.objects.count(), 1)
        self.assertEqual(
            FacilityClaim.objects.first().facility_workers_count, None
        )

    @override_switch("claim_a_facility", active=True)
    def test_facility_claim_with_empty_number_of_workers(self):
        self.__login()
        self.claim_data['number_of_workers'] = ''

        url = "/api/facilities/{}/claim/".format(self.facility.id)

        response = self.client.post(url, self.claim_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FacilityClaim.objects.count(), 1)
        self.assertEqual(
            FacilityClaim.objects.first().facility_workers_count, None
        )
