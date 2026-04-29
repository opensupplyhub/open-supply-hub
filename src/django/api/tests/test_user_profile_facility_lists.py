from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Contributor, FacilityList, Source, User


class TestUserProfileFacilityLists(APITestCase):
    def setUp(self):
        caches["view_cache"].clear()

        self.user_email = "owner@example.com"
        self.no_contrib_user_email = "no-contrib@example.com"

        self.user = User.objects.create(email=self.user_email)
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type="Brand / Retailer",
        )

        self.approved_list = FacilityList.objects.create(
            name="Approved List",
            header="country,name,address",
            file_name="approved.csv",
            status=FacilityList.APPROVED,
        )
        Source.objects.create(
            contributor=self.contributor,
            facility_list=self.approved_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
        )

        self.pending_list = FacilityList.objects.create(
            name="Pending List",
            header="country,name,address",
            file_name="pending.csv",
            status=FacilityList.PENDING,
        )
        Source.objects.create(
            contributor=self.contributor,
            facility_list=self.pending_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
        )

    def _url(self, pk):
        return f"/user-profile/{pk}/facility-lists/"

    def test_404_for_nonexistent_user(self):
        resp = self.client.get(self._url(999999))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_404_for_user_without_contributor(self):
        user_no_contrib = User.objects.create(email=self.no_contrib_user_email)
        resp = self.client.get(self._url(user_no_contrib.pk))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_only_approved_public_lists(self):
        resp = self.client.get(self._url(self.user.pk))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        names = [item["name"] for item in resp.data["results"]]
        self.assertIn("Approved List", names)
        self.assertNotIn("Pending List", names)
