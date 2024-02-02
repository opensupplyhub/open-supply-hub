import json

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point
from django.urls import reverse


class FacilityListItemTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility_list = FacilityList.objects.create(
            header="header", file_name="one", name="test list"
        )

        self.source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.facility_list,
            contributor=self.contributor,
        )

        statuses = [c[0] for c in FacilityListItem.STATUS_CHOICES]
        for i, possible_status in enumerate(statuses):
            FacilityListItem.objects.create(
                name="test name",
                address="test address",
                country_code="US",
                sector=["Apparel"],
                source=self.source,
                row_index=i,
                status=possible_status,
            )

        self.client.login(email=self.email, password=self.password)

    def test_get_all_items(self):
        response = self.client.get(
            reverse(
                "facility-list-items", kwargs={"pk": self.facility_list.pk}
            )
        )
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(
            len(FacilityListItem.STATUS_CHOICES), len(content["results"])
        )

    def test_get_items_filtered_by_status(self):
        url = reverse(
            "facility-list-items", kwargs={"pk": self.facility_list.pk}
        )

        response = self.client.get("{}?status=GEOCODED".format(url))
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(1, len(content["results"]))
        self.assertEqual("GEOCODED", content["results"][0]["status"])

    def test_get_multiple_statuses(self):
        url = reverse(
            "facility-list-items", kwargs={"pk": self.facility_list.pk}
        )

        response = self.client.get(
            "{}?status=GEOCODED&status=MATCHED".format(url)
        )
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(2, len(content["results"]))

    def test_invalid_status_returns_400(self):
        url = reverse(
            "facility-list-items", kwargs={"pk": self.facility_list.pk}
        )

        response = self.client.get("{}?status=FOO".format(url))
        self.assertEqual(400, response.status_code)
        content = json.loads(response.content)
        self.assertTrue("status" in content)

    def test_empty_status_filter_returns_400(self):
        url = reverse(
            "facility-list-items", kwargs={"pk": self.facility_list.pk}
        )
        response = self.client.get("{}?status=".format(url))
        self.assertEqual(400, response.status_code)
        content = json.loads(response.content)
        self.assertTrue("status" in content)

    def test_new_facility(self):
        url = reverse(
            "facility-list-items", kwargs={"pk": self.facility_list.pk}
        )

        # First assert that there are no NEW_FACILITYs in our test data.
        response = self.client.get("{}?status=NEW_FACILITY".format(url))
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(0, len(content["results"]))

        # Create a facility from the test list item
        list_item = FacilityListItem.objects.filter(
            source=self.source,
            status=FacilityListItem.MATCHED,
        ).first()
        facility = Facility.objects.create(
            country_code=list_item.country_code,
            created_from=list_item,
            location=Point(0, 0),
        )
        list_item.facility = facility
        list_item.save()

        # Assert that we now have a NEW_FACILITY
        response = self.client.get("{}?status=NEW_FACILITY".format(url))
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(1, len(content["results"]))
