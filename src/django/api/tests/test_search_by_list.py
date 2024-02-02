import json

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class SearchByListTest(APITestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.superuser_email = "super@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor = Contributor.objects.create(
            id=111,
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            id=123, header="header", file_name="one", name="First List"
        )

        self.source = Source.objects.create(
            id=456,
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            id=789,
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            id="US2021067MMRTSD",
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=self.list_item,
            confidence=0.85,
            results="",
        )

        self.list_item.facility = self.facility
        self.list_item.save()

    def test_fetched_by_contributor(self):
        url = "/api/facilities/?contributors={}".format(self.contributor.id)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_fetched_by_list(self):
        url = "/api/facilities/?lists={}".format(self.list.id)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_fetched_by_list_and_contributor(self):
        url = "/api/facilities/?contributors={}&lists={}".format(
            self.contributor.id, self.list.id
        )
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)
