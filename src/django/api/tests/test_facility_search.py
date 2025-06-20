import json

from api.models import (
    Contributor,
    Facility,
    FacilityAlias,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point
from django.urls import reverse


class FacilitySearchTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(FacilitySearchTest, self).setUp()

        self.user_two_email = "two@example.com"
        self.user_two_password = "example123"
        self.user_two = User.objects.create(email=self.user_two_email)
        self.user_two.set_password(self.user_two_password)
        self.user_two.save()

        self.contributor_two = Contributor.objects.create(
            admin=self.user_two,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_two = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        self.source_two = Source.objects.create(
            facility_list=self.list_two,
            source_type=Source.LIST,
            contributor=self.contributor_two,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
        )

        self.facility_two = Facility.objects.create(
            name="Name Two",
            address="Address Two",
            country_code="US",
            location=Point(5, 5),
            created_from=self.list_item_two,
        )

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_two,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results="",
        )

        self.list_item_two.facility = self.facility_two
        self.list_item_two.save()

        self.source_two_b = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.contributor
        )

        self.list_item_two_b = FacilityListItem.objects.create(
            name="Item 2b",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two_b,
        )

        self.match_two_b = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_two,
            facility_list_item=self.list_item_two_b,
            confidence=0.85,
            results="",
        )

        self.list_item_two_b.facility = self.facility_two
        self.list_item_two_b.save()

        self.alias = FacilityAlias.objects.create(
            facility=self.facility_two, os_id="US1234567ABCDEF"
        )

        self.base_url = reverse("facility-list")
        self.contributor_or_url = (
            self.base_url + "?contributors={}&contributors={}"
        )
        self.contributor_and_url = (
            self.base_url
            + "?contributors={}&contributors={}&combine_contributors=AND"
        )

        self.client.login(email=self.user_email, password=self.user_password)

    def assert_response_count(self, response, count):
        data = json.loads(response.content)
        self.assertEqual(count, int(data["count"]))

    def test_contributor_or_search(self):
        response = self.client.get(
            self.contributor_or_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 2)

    def test_contributor_and_search(self):
        response = self.client.get(
            self.contributor_and_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 1)

    def test_contributor_and_inactive_match(self):
        self.match_two_b.is_active = False
        self.match_two_b.save()

        response = self.client.get(
            self.contributor_and_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 0)

    def test_contributor_and_inactive_source(self):
        self.source_two_b.is_active = False
        self.source_two_b.save()

        response = self.client.get(
            self.contributor_and_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 0)

    def test_contributor_and_private_source(self):
        self.source_two_b.is_public = False
        self.source_two_b.save()

        response = self.client.get(
            self.contributor_and_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 0)

    def test_contributor_and_pending_match(self):
        self.match_two_b.status = FacilityMatch.PENDING
        self.match_two_b.save()

        response = self.client.get(
            self.contributor_and_url.format(
                self.contributor.id, self.contributor_two.id
            )
        )
        self.assert_response_count(response, 0)

    def test_search_aliased_id(self):
        response = self.client.get(
            "{}?q={}".format(self.base_url, self.alias.os_id)
        )

        self.assert_response_count(response, 1)

        response_json = json.loads(response.content)
        self.assertEqual(
            self.alias.facility.id, response_json["features"][0]["id"]
        )
