import json

from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityAlias,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
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
        partner_field_name_one = "partner_or_field_one"
        partner_field_name_two = "partner_or_field_two"
        field_one = PartnerField.objects.create(
            name=partner_field_name_one,
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        field_two = PartnerField.objects.create(
            name=partner_field_name_two,
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        contributor_one.partner_fields.add(field_one)
        contributor_two.partner_fields.add(field_two)

        ExtendedField.objects.create(
            contributor=contributor_one,
            facility=self.facility,
            field_name=partner_field_name_one,
            value={"min": 1, "max": 1},
        )
        ExtendedField.objects.create(
            contributor=contributor_two,
            facility=self.facility_two,
            field_name=partner_field_name_two,
            value={"raw_values": ["Yarn"]},
        )

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 2)

    def test_partner_contributor_ignores_inactive_partner_fields(
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
        active_partner_field_name = "partner_active_field"
        inactive_partner_field_name = "partner_inactive_field"
        active_field = PartnerField.objects.create(
            name=active_partner_field_name,
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        inactive_field = (
            PartnerField.objects.get_all_including_inactive().create(
                name=inactive_partner_field_name,
                type=PartnerField.STRING,
                group=group,
                active=False,
            )
        )
        contributor_one.partner_fields.add(active_field)
        contributor_two.partner_fields.add(inactive_field)

        ExtendedField.objects.create(
            contributor=contributor_one,
            facility=self.facility,
            field_name=active_partner_field_name,
            value={"raw_values": ["Facility One"]},
        )
        ExtendedField.objects.create(
            contributor=contributor_two,
            facility=self.facility_two,
            field_name=inactive_partner_field_name,
            value={"raw_values": ["Inactive-only Facility"]},
        )

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 1)

        response_json = json.loads(response.content)
        self.assertEqual(
            self.facility.id, response_json["features"][0]["id"]
        )

    def test_partner_contributor_no_active_grouped_fields_returns_none(
        self
    ):
        group = PartnerFieldGroup.objects.create(
            name="Inactive Group", order=4
        )
        contributor_one = self._create_partner_contributor(
            "partner-none-one@example.com", "Partner None One"
        )
        contributor_two = self._create_partner_contributor(
            "partner-none-two@example.com", "Partner None Two"
        )
        inactive_field_one = (
            PartnerField.objects.get_all_including_inactive().create(
                name="partner_inactive_none_one",
                type=PartnerField.STRING,
                group=group,
                active=False,
            )
        )
        inactive_field_two = (
            PartnerField.objects.get_all_including_inactive().create(
                name="partner_inactive_none_two",
                type=PartnerField.STRING,
                group=group,
                active=False,
            )
        )
        contributor_one.partner_fields.add(inactive_field_one)
        contributor_two.partner_fields.add(inactive_field_two)

        response = self.client.get(
            "{}?partner_contributor={}&partner_contributor={}".format(
                self.base_url, contributor_one.id, contributor_two.id
            )
        )
        self.assert_response_count(response, 0)

    def test_partner_contributor_ignores_cross_contributor_field_name(
        self
    ):
        group = PartnerFieldGroup.objects.create(
            name="Cross Contributor Isolation Group", order=5
        )
        contributor_one = self._create_partner_contributor(
            "partner-cross-one@example.com", "Partner Cross One"
        )
        contributor_two = self._create_partner_contributor(
            "partner-cross-two@example.com", "Partner Cross Two"
        )

        partner_field_name_one = "partner_cross_field_one"
        partner_field_name_two = "partner_cross_field_two"
        field_one = PartnerField.objects.create(
            name=partner_field_name_one,
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        field_two = PartnerField.objects.create(
            name=partner_field_name_two,
            type=PartnerField.STRING,
            group=group,
            active=True,
        )
        contributor_one.partner_fields.add(field_one)
        contributor_two.partner_fields.add(field_two)

        # This is intentionally invalid data: contributor_one writes a value
        # under contributor_two's field name. We keep this test to document
        # the bad input and ensure it does not leak into contributor_two
        # filtering results.
        ExtendedField.objects.create(
            contributor=contributor_one,
            facility=self.facility,
            field_name=partner_field_name_two,
            value={"raw_values": ["Wrong contributor-field pairing"]},
        )

        response = self.client.get(
            "{}?partner_contributor={}".format(
                self.base_url, contributor_two.id
            )
        )
        self.assert_response_count(response, 0)
