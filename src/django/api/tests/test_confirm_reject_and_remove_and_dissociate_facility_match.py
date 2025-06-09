from api.constants import MatchResponsibility
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse


class ConfirmRejectAndRemoveAndDissociateFacilityMatchTest(TestCase):
    def setUp(self):
        self.country_code = "US"

        self.prior_user_name = "prior_user_name"
        self.prior_user_email = "prioruser@example.com"
        self.prior_contrib_name = "prior_contrib_name"
        self.prior_list_name = "prior_list_name"
        self.prior_user = User.objects.create(email=self.prior_user_email)
        self.prior_address_one = "prior_address_one"
        self.prior_address_two = "prior_address_two"
        self.prior_name_one = "prior_name_one"
        self.prior_name_two = "prior_name_two"
        self.prior_user_password = "example-password"
        self.prior_user.set_password(self.prior_user_password)
        self.prior_user.save()

        self.prior_contrib = Contributor.objects.create(
            admin=self.prior_user,
            name=self.prior_contrib_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.prior_list = FacilityList.objects.create(
            header="header", file_name="one", name=self.prior_list_name
        )

        self.prior_source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.prior_list,
            contributor=self.prior_contrib,
        )

        self.prior_list_item_one = FacilityListItem.objects.create(
            name=self.prior_name_one,
            address=self.prior_address_one,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.prior_source,
        )

        self.prior_facility_one = Facility.objects.create(
            name=self.prior_list_item_one.name,
            address=self.prior_list_item_one.address,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.prior_list_item_one,
        )

        self.prior_facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.prior_facility_one,
            results="",
            facility_list_item=self.prior_list_item_one,
        )

        self.prior_list_item_two = FacilityListItem.objects.create(
            name=self.prior_name_two,
            address=self.prior_address_two,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index=2,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.prior_source,
        )

        self.prior_facility_two = Facility.objects.create(
            name=self.prior_list_item_two.name,
            address=self.prior_list_item_two.address,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.prior_list_item_two,
        )

        self.prior_facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.prior_facility_two,
            results="",
            facility_list_item=self.prior_list_item_one,
        )

        self.current_user_name = "current_user_name"
        self.current_user_email = "currentuser@example.com"
        self.current_contrib_name = "current_contrib_name"
        self.current_list_name = "current_list_name"
        self.current_user = User.objects.create(email=self.current_user_email)
        self.current_user_password = "password123"
        self.current_user.set_password(self.current_user_password)
        self.current_user.save()

        self.superuser = User.objects.create_superuser(
            "superuser@example.com", "superuser"
        )

        self.current_address = "current_address"
        self.current_name = "current_name"

        self.current_contrib = Contributor.objects.create(
            admin=self.current_user,
            name=self.current_contrib_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.current_list = FacilityList.objects.create(
            header="header",
            file_name="one",
            name=self.current_list_name,
            match_responsibility=MatchResponsibility.CONTRIBUTOR,
        )

        self.current_source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.current_list,
            contributor=self.current_contrib,
        )

        self.current_list_item = FacilityListItem.objects.create(
            name=self.current_name,
            address=self.current_address,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.current_source,
        )

        self.potential_facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.prior_facility_one,
            results="",
            facility_list_item=self.current_list_item,
        )

        self.potential_facility_match_two = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.prior_facility_two,
            results="",
            facility_list_item=self.current_list_item,
        )

        self.client.login(
            email=self.current_user_email, password=self.current_user_password
        )

        self.remove_url = "/api/facility-lists/{}/remove/".format(
            self.current_list.id
        )

    def match_url(self, match, action="detail"):
        return reverse(
            "facility-match-{}".format(action), kwargs={"pk": match.pk}
        )

    def test_confirming_match_rejects_other_potential_matches(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(confirmed_match.status, FacilityMatch.CONFIRMED)
        self.assertEqual(rejected_match.status, FacilityMatch.REJECTED)

    def test_confirming_match_changes_list_item_status(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        updated_list_item = FacilityListItem.objects.get(
            pk=self.current_list_item.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(
            updated_list_item.status, FacilityListItem.CONFIRMED_MATCH
        )

    def test_confirming_match_doesnt_create_new_facility(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        facilities = Facility.objects.all()

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(facilities.count(), 2)

    def test_rejecting_last_potential_match_changes_list_item_status(self):
        reject_response_one = self.client.post(
            self.match_url(self.potential_facility_match_one, action="reject")
        )

        reject_response_two = self.client.post(
            self.match_url(self.potential_facility_match_two, action="reject")
        )

        self.assertEqual(reject_response_one.status_code, 200)
        self.assertEqual(reject_response_two.status_code, 200)

        updated_list_item = FacilityListItem.objects.get(
            pk=self.current_list_item.id
        )

        self.assertEqual(
            updated_list_item.status, FacilityListItem.CONFIRMED_MATCH
        )

    def test_rejecting_one_of_several_matches_changes_match_to_rejected(self):
        reject_response_one = self.client.post(
            self.match_url(self.potential_facility_match_one, action="reject")
        )

        self.assertEqual(reject_response_one.status_code, 200)

        updated_potential_match_one = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        self.assertEqual(
            updated_potential_match_one.status, FacilityMatch.REJECTED
        )

        updated_potential_match_two = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(
            updated_potential_match_two.status, FacilityMatch.PENDING
        )

    def test_rejecting_one_of_several_matches_doesnt_change_item_status(self):
        reject_response_one = self.client.post(
            self.match_url(self.potential_facility_match_one, action="reject")
        )

        self.assertEqual(reject_response_one.status_code, 200)

        updated_list_item = FacilityListItem.objects.get(
            pk=self.current_list_item.id
        )

        self.assertEqual(
            updated_list_item.status, FacilityListItem.POTENTIAL_MATCH
        )

    def test_rejecting_last_potential_match_creates_new_facility(self):
        reject_response_one = self.client.post(
            self.match_url(self.potential_facility_match_one, action="reject")
        )

        reject_response_two = self.client.post(
            self.match_url(self.potential_facility_match_two, action="reject")
        )

        self.assertEqual(reject_response_one.status_code, 200)
        self.assertEqual(reject_response_two.status_code, 200)

        facilities = Facility.objects.all()
        self.assertEqual(facilities.count(), 3)

    def test_rejecting_last_potential_match_creates_a_new_facility_match(self):
        initial_facility_matches_count = FacilityMatch.objects.all().count()

        reject_response_one = self.client.post(
            self.match_url(self.potential_facility_match_one, action="reject")
        )

        reject_response_two = self.client.post(
            self.match_url(self.potential_facility_match_two, action="reject")
        )

        self.assertEqual(reject_response_one.status_code, 200)
        self.assertEqual(reject_response_two.status_code, 200)

        facilities = Facility.objects.all()
        self.assertEqual(facilities.count(), 3)

        new_facility_matches_count = FacilityMatch.objects.all().count()
        self.assertEqual(
            initial_facility_matches_count + 1,
            new_facility_matches_count,
        )

    def test_removing_a_list_item_sets_its_matches_to_inactive(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(confirmed_match.status, FacilityMatch.CONFIRMED)
        self.assertEqual(rejected_match.status, FacilityMatch.REJECTED)
        self.assertEqual(confirmed_match.is_active, True)
        self.assertEqual(rejected_match.is_active, True)

        remove_response = self.client.post(
            self.remove_url,
            {"list_item_id": self.current_list_item.id},
        )

        self.assertEqual(remove_response.status_code, 200)

        updated_confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        updated_rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(updated_confirmed_match.is_active, False)
        self.assertEqual(updated_rejected_match.is_active, False)

    def test_only_list_contribtutor_can_remove_a_list_item(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(confirmed_match.status, FacilityMatch.CONFIRMED)
        self.assertEqual(rejected_match.status, FacilityMatch.REJECTED)
        self.assertEqual(confirmed_match.is_active, True)
        self.assertEqual(rejected_match.is_active, True)

        self.client.logout()

        self.client.login(
            email=self.prior_user_email, password=self.prior_user_password
        )

        remove_response = self.client.post(
            self.remove_url,
            {"list_item_id": self.current_list_item.id},
        )

        self.assertEqual(remove_response.status_code, 404)

    def test_superuser_can_remove_list_item(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(confirmed_match.status, FacilityMatch.CONFIRMED)
        self.assertEqual(rejected_match.status, FacilityMatch.REJECTED)
        self.assertEqual(confirmed_match.is_active, True)
        self.assertEqual(rejected_match.is_active, True)

        self.client.logout()

        self.client.login(email="superuser@example.com", password="superuser")

        remove_response = self.client.post(
            self.remove_url,
            {"list_item_id": self.current_list_item.id},
        )

        self.assertEqual(remove_response.status_code, 200)

        updated_confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        updated_rejected_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_two.id
        )

        self.assertEqual(updated_confirmed_match.is_active, False)
        self.assertEqual(updated_rejected_match.is_active, False)

    def test_dissociate_sets_matches_to_inactive(self):
        confirm_response = self.client.post(
            self.match_url(self.potential_facility_match_one, action="confirm")
        )

        confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(confirmed_match.is_active, True)

        dissociate_url = reverse(
            "facility-dissociate", kwargs={"pk": confirmed_match.facility.pk}
        )
        dissociate_response = self.client.post(dissociate_url)

        self.assertEqual(dissociate_response.status_code, 200)

        updated_confirmed_match = FacilityMatch.objects.get(
            pk=self.potential_facility_match_one.id
        )

        self.assertEqual(updated_confirmed_match.is_active, False)
