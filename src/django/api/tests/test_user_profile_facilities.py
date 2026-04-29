from django.contrib.gis.geos import Point
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Contributor, User
from api.models.facility.facility_index import FacilityIndex


class TestUserProfileFacilities(APITestCase):
    def setUp(self):
        caches["view_cache"].clear()
        self.user_email = "test@example.com"
        self.other_user_email = "other@example.com"
        self.no_contrib_user_email = "no-contrib@example.com"

        self.user = User.objects.create(email=self.user_email)
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility = FacilityIndex.objects.create(
            id="US2021250D1DTN7",
            name="Test Facility",
            address="123 Main St",
            country_code="US",
            location=Point(0, 0),
            contributors_count=1,
            contributors_id=[self.contributor.id],
            contributors=[{"id": self.contributor.id, "name": "Test"}],
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{"address": "123 Main St"}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def _url(self, pk):
        return f"/user-profile/{pk}/facilities/"

    def test_returns_404_for_nonexistent_user(self):
        response = self.client.get(self._url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_404_for_user_without_contributor(self):
        user_no_contrib = User.objects.create(email=self.no_contrib_user_email)
        response = self.client.get(self._url(user_no_contrib.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_facilities_for_valid_user(self):
        response = self.client.get(self._url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        features = response.data["results"]["features"]
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["id"], self.facility.id)

    def test_returns_empty_for_user_with_no_facilities(self):
        other_user = User.objects.create(email=self.other_user_email)
        Contributor.objects.create(
            admin=other_user,
            name="Other Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        response = self.client.get(self._url(other_user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]["features"]), 0)
