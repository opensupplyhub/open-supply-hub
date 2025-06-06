import json

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
            source_uuid=self.source_one,
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
