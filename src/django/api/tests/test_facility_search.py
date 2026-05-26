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
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

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

    def _set_index_field_names(self, facility, field_names):
        facility_index = FacilityIndex.objects.get(id=facility.id)
        facility_index.extended_fields = [
            {"field_name": field_name} for field_name in field_names
        ]
        facility_index.save()

    def _create_partner_contributor(self, email, name):
        user = User.objects.create(email=email)
        user.set_password("example123")
        user.save()
        return Contributor.objects.create(
            admin=user,
            name=name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

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

    def test_partner_contributor_or_search(self):
        group = PartnerFieldGroup.objects.create(name="Group OR", order=1)
        contributor_one = self._create_partner_contributor(
            "partner-or-one@example.com", "Partner OR One"
        )
        contributor_two = self._create_partner_contributor(
            "partner-or-two@example.com", "Partner OR Two"
        )
        field_one = PartnerField.objects.create(
            name="partner_or_field_one",
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        field_two = PartnerField.objects.create(
            name="partner_or_field_two",
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        contributor_one.partner_fields.add(field_one)
        contributor_two.partner_fields.add(field_two)

        self._set_index_field_names(self.facility, ["partner_or_field_one"])
        self._set_index_field_names(
            self.facility_two, ["partner_or_field_two"]
        )

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 2)

    def test_partner_contributor_and_search(self):
        group = PartnerFieldGroup.objects.create(name="Group AND", order=2)
        contributor_one = self._create_partner_contributor(
            "partner-and-one@example.com", "Partner AND One"
        )
        contributor_two = self._create_partner_contributor(
            "partner-and-two@example.com", "Partner AND Two"
        )
        field_one = PartnerField.objects.create(
            name="partner_and_field_one",
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        field_two = PartnerField.objects.create(
            name="partner_and_field_two",
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        contributor_one.partner_fields.add(field_one)
        contributor_two.partner_fields.add(field_two)

        self._set_index_field_names(self.facility, ["partner_and_field_one"])
        self._set_index_field_names(
            self.facility_two,
            ["partner_and_field_one", "partner_and_field_two"],
        )

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}"
            "&combine_partner_contributors=AND".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 1)

        response_json = json.loads(response.content)
        self.assertEqual(
            self.facility_two.id, response_json["features"][0]["id"]
        )

    def test_partner_contributor_and_missing_active_fields_returns_none(
        self
    ):
        group = PartnerFieldGroup.objects.create(
            name="Group Missing Active Field", order=3
        )
        contributor_one = self._create_partner_contributor(
            "partner-and-missing-one@example.com", "Partner Missing One"
        )
        contributor_two = self._create_partner_contributor(
            "partner-and-missing-two@example.com", "Partner Missing Two"
        )
        active_field = PartnerField.objects.create(
            name="partner_active_field",
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        inactive_field = (
            PartnerField.objects.get_all_including_inactive().create(
                name="partner_inactive_field",
                type=PartnerField.STRING,
                group=group,
                active=False,
            )
        )
        contributor_one.partner_fields.add(active_field)
        contributor_two.partner_fields.add(inactive_field)

        self._set_index_field_names(self.facility, ["partner_active_field"])
        self._set_index_field_names(
            self.facility_two, ["partner_active_field"]
        )

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}"
            "&combine_partner_contributors=AND".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 0)
