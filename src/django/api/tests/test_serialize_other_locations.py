import json

from api.constants import UpdateLocationParams
from api.models import (
    Contributor,
    ExtendedField,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point


class SerializeOtherLocationsTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(SerializeOtherLocationsTest, self).setUp()
        self.url = "/api/facilities/{}".format(self.facility.id)

        self.other_user_email = "hello@example.com"
        self.other_user_password = "example123"
        self.other_user = User.objects.create(email=self.other_user_email)
        self.other_user.set_password(self.other_user_password)
        self.other_user.save()

        self.other_contributor = Contributor.objects.create(
            admin=self.other_user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.assertFalse(
            self.other_contributor.id == self.other_user.id,
            "We want to verify that we serialize the proper ID "
            "and we can only do that if we have distinct "
            "Contributor and User ID values.",
        )

        self.other_list = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        self.other_source = Source.objects.create(
            facility_list=self.other_list,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )

        self.other_list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(5, 5),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.other_source,
            facility=self.facility,
            source_uuid=self.other_source,
        )

        self.other_match = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            facility_list_item=self.other_list_item,
            confidence=0.85,
            results="",
        )

        self.extended_field_one = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name one",
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            is_verified=True,
        )

        self.extended_field_two = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name two",
            contributor=self.other_contributor,
            facility=self.facility,
            facility_list_item=self.other_list_item,
        )

        self.extended_field_three = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name two",
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
        )

    def test_excludes_match_if_geocoded_point_is_none(self):
        self.other_list_item.geocoded_point = None
        self.other_list_item.save()
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )
        data = json.loads(response.content)
        self.assertEqual(
            len(data["properties"]["other_locations"]),
            0,
        )

    def test_serializes_other_match_location_in_facility_details(self):
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )

        data = json.loads(response.content)
        self.assertEqual(
            len(data["properties"]["other_locations"]),
            1,
        )

        self.assertIsNone(
            data["properties"]["other_locations"][0]["notes"],
        )

        self.assertEqual(
            data["properties"]["other_locations"][0]["lat"],
            5,
        )

        # The UI needs to build profile page links that use the ID of the User
        # who is the "admin" of the Contributor, not the ID of the Contributor
        # itself.
        self.assertEqual(
            data["properties"]["other_locations"][0]["contributor_id"],
            self.other_user.id,
        )

    def test_does_not_serialize_inactive_list_item_matches(self):
        self.other_source.is_active = False
        self.other_source.save()
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )

        data = json.loads(response.content)
        self.assertEqual(
            len(data["properties"]["other_locations"]),
            0,
        )

    def test_does_not_serialize_non_public_list_item_matches(self):
        self.other_source.is_public = False
        self.other_source.save()
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )

        data = json.loads(response.content)
        self.assertEqual(
            len(data["properties"]["other_locations"]),
            0,
        )

    def test_serializes_other_locations_in_facility_details(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        self.client.post(
            "/api/facilities/{}/update-location/".format(self.facility.id),
            {
                UpdateLocationParams.LAT: 41,
                UpdateLocationParams.LNG: 43,
                UpdateLocationParams.NOTES: "A note",
                UpdateLocationParams.CONTRIBUTOR_ID: self.other_contributor.id,
            },
        )

        self.client.logout()

        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )

        data = json.loads(response.content)
        self.assertEqual(
            len(data["properties"]["other_locations"]),
            3,
        )

        self.assertEqual(
            data["properties"]["other_locations"][0]["notes"],
            "A note",
        )

        # The UI needs to build profile page links that use the ID of the User
        # who is the "admin" of the Contributor, not the ID of the Contributor
        # itself.
        self.assertEqual(
            data["properties"]["other_locations"][0]["contributor_id"],
            self.other_user.id,
        )

    def test_serializes_other_location_without_note_or_contributor(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        self.client.post(
            "/api/facilities/{}/update-location/".format(self.facility.id),
            {
                UpdateLocationParams.LAT: 41,
                UpdateLocationParams.LNG: 43,
                UpdateLocationParams.NOTES: "",
            },
        )

        self.client.logout()

        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )

        data = json.loads(response.content)

        self.assertEqual(
            len(data["properties"]["other_locations"]),
            3,
        )

        self.assertEqual(
            data["properties"]["other_locations"][0]["notes"],
            "",
        )

        self.assertEqual(
            data["properties"]["other_locations"][0]["contributor_name"],
            None,
        )

    def test_serializes_extended_fields_in_facility_details(self):
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )
        data = json.loads(response.content)
        fields = data["properties"]["extended_fields"]["native_language_name"]

        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0]["value"], "name one")

    def test_serializes_extended_fields_sorts_verified_first(self):
        self.extended_field_one.is_verified = False
        self.extended_field_one.save()

        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )
        data = json.loads(response.content)
        fields = data["properties"]["extended_fields"]["native_language_name"]

        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0]["value"], "name two")

    def test_serializes_extended_fields_drops_inactive(self):
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )
        data = json.loads(response.content)
        fields = data["properties"]["extended_fields"]["native_language_name"]

        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[1]["value"], "name two")
        self.assertEqual(fields[1]["value_count"], 2)

        self.source.is_active = False
        self.source.save()
        response = self.client.get(
            "/api/facilities/{}/".format(self.facility.id)
        )
        data = json.loads(response.content)
        fields = data["properties"]["extended_fields"]["native_language_name"]

        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0]["value"], "name two")
        self.assertEqual(fields[0]["value_count"], 1)

    def test_serializes_extended_fields_inactive_isnt_counted(self):
        self.extended_field_two.facility_list_item.source.is_active = False
        self.extended_field_two.facility_list_item.source.save()
