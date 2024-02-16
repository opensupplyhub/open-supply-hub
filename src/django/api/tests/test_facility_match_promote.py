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


class FacilityMatchPromoteTest(APITestCase):
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

        self.address_one = "Address One"
        self.address_two = "Address Two"
        self.name_one = "Name One"
        self.name_two = "Name Two"
        self.country_code_one = "US"
        self.country_code_two = "CA"
        self.location_one = Point(1, 1)
        self.location_two = Point(2, 2)

        self.list_item_one = FacilityListItem.objects.create(
            name=self.name_one,
            address=self.name_one,
            country_code=self.country_code_one,
            sector=["Apparel"],
            row_index=1,
            geocoded_point=self.location_one,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
        )

        self.facility_one = Facility.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code_one,
            location=self.location_one,
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
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name=self.name_two,
            address=self.address_two,
            country_code=self.country_code_two,
            sector=["Apparel"],
            row_index=1,
            geocoded_point=self.location_two,
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

        self.list_item_three = FacilityListItem.objects.create(
            name="third facility",
            address="third address",
            country_code="US",
            sector=["Apparel"],
            source=self.source_one,
            row_index=2,
            geocoded_point=Point(3, 3),
            status=FacilityListItem.MATCHED,
        )

        self.other_facility = Facility.objects.create(
            name="third facility",
            address="third address",
            country_code="US",
            location=Point(3, 3),
            created_from=self.list_item_three,
        )

        self.list_item_three.facility = self.other_facility
        self.list_item_three.save()

        self.list_item_two.facility = self.facility_one
        self.list_item_two.save()

        self.promote_url = "/api/facilities/{}/promote/".format(
            self.facility_one.id,
        )

    def test_promote_is_unauthorized_for_anon_users(self):
        post_response = self.client.post(self.promote_url)
        self.assertEqual(post_response.status_code, 401)

    def test_promote_is_unauth_for_non_admins(self):
        self.client.login(
            email=self.user_one_email, password=self.user_one_password
        )
        post_response = self.client.post(self.promote_url)
        self.assertEqual(post_response.status_code, 403)

    def test_returns_error_if_list_item_not_in_matched_status(self):
        self.list_item_two.status = FacilityListItem.PARSED
        self.list_item_two.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.promote_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 400)

    def test_returns_error_if_match_is_not_to_facility(self):
        self.match_two.facility = self.other_facility
        self.match_two.facility_list_item = self.list_item_three
        self.match_two.save()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        post_response = self.client.post(
            self.promote_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 400)

    def test_returns_error_if_facility_created_from_match_list_item(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        post_response = self.client.post(
            self.promote_url, {"match_id": self.match_one.id}
        )
        self.assertEqual(post_response.status_code, 400)

    def test_updates_facility_if_list_item_is_in_matched_status(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.promote_url, {"match_id": self.match_two.id}
        )
        self.assertEqual(post_response.status_code, 200)

        self.facility_one.refresh_from_db()

        self.assertEqual(
            self.facility_one.name,
            self.list_item_two.name,
        )

        self.assertEqual(
            self.facility_one.address,
            self.list_item_two.address,
        )

        self.assertEqual(
            self.facility_one.country_code,
            self.list_item_two.country_code,
        )

        self.assertEqual(
            self.facility_one.location,
            self.list_item_two.geocoded_point,
        )

        reason = "Promoted item {} in list {} over item {} in list {}".format(
            self.list_item_two.id,
            self.list_two.id,
            self.list_item_one.id,
            self.list_one.id,
        )

        self.assertEqual(
            Facility.history.first().history_change_reason,
            reason,
        )

    def test_can_promote_single_item_over_list_item(self):
        single_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        single_item = FacilityListItem.objects.create(
            name="single",
            address="single",
            country_code="US",
            sector=["Apparel"],
            row_index=0,
            geocoded_point=self.location_one,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=single_source,
        )

        single_match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_one,
            facility_list_item=single_item,
            confidence=0.85,
            results="",
        )

        single_item.facility = self.facility_one
        single_item.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        post_response = self.client.post(
            self.promote_url, {"match_id": single_match.id}
        )
        self.assertEqual(post_response.status_code, 200)
