import json

from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.user import User
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class FacilitySplitTest(APITestCase):
    def setUp(self):
        self.user_one_email = "one@example.com"
        self.user_one_password = "example123"
        self.user_one = User.objects.create(email=self.user_one_email)
        self.user_one.set_password(self.user_one_password)
        self.user_one.save()

        self.user_two_email = "two@example.com"
        self.user_two_password = "example123"
        self.user_two = User.objects.create(email=self.user_two_email)
        self.user_two.set_password(self.user_two_password)
        self.user_two.save()

        self.superuser_email = "super@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor_one = Contributor.objects.create(
            admin=self.user_one,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_one,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
        )

        self.facility_one = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.match_one = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_one,
            facility_list_item=self.list_item_one,
            confidence=0.85,
            results="",
        )

        self.list_item_one.facility = self.facility_one
        self.list_item_one.save()

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

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_one,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results="",
        )

        self.list_item_two.facility = self.facility_one
        self.list_item_two.save()

        self.extended_field_one = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name one",
            contributor=self.contributor_one,
            facility=self.facility_one,
            facility_list_item=self.list_item_one,
            is_verified=True,
        )

        self.extended_field_two = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name two",
            contributor=self.contributor_two,
            facility=self.facility_one,
            facility_list_item=self.list_item_two,
        )

        self.split_url = "/api/facilities/{}/split/".format(
            self.facility_one.id,
        )

    def test_split_is_unauthorized_for_anonymous_users(self):
        get_response = self.client.get(self.split_url)
        self.assertEqual(get_response.status_code, 401)

        post_response = self.client.post(self.split_url)
        self.assertEqual(post_response.status_code, 401)

    def test_split_is_unauthorized_for_non_administrators(self):
        self.client.login(
            email=self.user_one_email, password=self.user_one_password
        )
        get_response = self.client.get(self.split_url)
        self.assertEqual(get_response.status_code, 403)

        post_response = self.client.post(self.split_url)
        self.assertEqual(post_response.status_code, 403)

    def test_get_returns_facility_details_with_match_data(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        get_response = self.client.get(self.split_url)
        self.assertEqual(get_response.status_code, 200)

        data = json.loads(get_response.content)
        self.assertEqual(
            len(data["properties"]["matches"]),
            1,
        )

        self.assertEqual(
            data["properties"]["matches"][0]["match_id"],
            self.match_two.id,
        )

    def test_post_returns_bad_request_without_match_id(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(self.split_url, {})
        self.assertEqual(post_response.status_code, 400)

    def test_post_reverts_to_created_facility(self):
        self.facility_two = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_two,
        )

        initial_facility_count = Facility.objects.all().count()
        self.assertEqual(initial_facility_count, 2)
        self.assertEqual(self.match_two.facility, self.facility_one)

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)

        updated_facility_count = Facility.objects.all().count()

        self.assertEqual(updated_facility_count, initial_facility_count)

        self.match_two.refresh_from_db()
        self.assertEqual(self.match_two.facility, self.facility_two)

    def test_post_creates_a_new_facility(self):
        initial_facility_count = Facility.objects.all().count()
        self.assertEqual(initial_facility_count, 1)

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)

        updated_facility_count = Facility.objects.all().count()

        self.assertEqual(updated_facility_count, 2)

    def test_post_decrements_prior_facility_matches(self):
        self.assertEqual(
            self.facility_one.facilitymatch_set.count(),
            2,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)

        self.facility_one.refresh_from_db()

        self.assertEqual(
            self.facility_one.facilitymatch_set.count(),
            1,
        )

    def test_post_returns_match_id_and_new_os_id(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)

        data = json.loads(post_response.content)

        self.assertEqual(
            self.match_two.id,
            data["match_id"],
        )

        self.match_two.refresh_from_db()

        self.assertEqual(
            self.match_two.facility.id,
            data["new_os_id"],
        )

    def test_post_updates_extended_fields(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)
        data = json.loads(post_response.content)
        new_facility_id = data["new_os_id"]

        # Fields not associated with the split-off match should be unchanged
        self.extended_field_one.refresh_from_db()
        self.assertEqual(self.extended_field_one.facility, self.facility_one)
        self.assertEqual(
            self.extended_field_one.facility_list_item, self.list_item_one
        )

        # Field associated with the split-off match should be updated
        self.extended_field_two.refresh_from_db()
        self.assertEqual(self.extended_field_two.facility.id, new_facility_id)
        self.assertEqual(
            self.extended_field_two.facility_list_item, self.list_item_two
        )

    def test_post_updates_facility_index(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.split_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)
        data = json.loads(post_response.content)
        new_facility_id = data["new_os_id"]

        facility_index_one = FacilityIndex.objects.get(id=self.facility_one.id)
        self.assertIn(
            self.extended_field_one.value,
            facility_index_one.native_language_name,
        )
        self.assertNotIn(
            self.extended_field_two.value,
            facility_index_one.native_language_name,
        )
        facility_index_two = FacilityIndex.objects.get(id=new_facility_id)
        self.assertNotIn(
            self.extended_field_one.value,
            facility_index_two.native_language_name,
        )
        self.assertIn(
            self.extended_field_two.value,
            facility_index_two.native_language_name,
        )
