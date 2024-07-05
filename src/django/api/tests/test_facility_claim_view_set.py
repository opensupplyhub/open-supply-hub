from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.core import mail


class FacilityClaimViewSetTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.superuser = User.objects.create_superuser(
            "superuser@example.com", "superuser"
        )

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="List"
        )

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.facility_claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="Name",
            phone_number=12345,
            company_name="Test",
            website="http://example.com",
            facility_description="description",
        )

        self.update_claim_data = {
            "facility_description": "description",
            "facility_phone_number_publicly_visible": False,
            "office_info_publicly_visible": False,
            "point_of_contact_publicly_visible": False,
            "facility_website_publicly_visible": False,
        }

        self.update_claim_url = "/api/facility-claims/{}/claimed/".format(
            self.facility_claim.id
        )

    def __login_superuser(self):
        self.client.login(email="superuser@example.com", password="superuser")

    def __login_contributor(self):
        self.client.login(username='test@example.com', password='example123')

    def __post_message_claimant(self, claim_id, message):
        return self.client.post(
            "/api/facility-claims/{}/message-claimant/".format(claim_id),
            {"message": message},
        )

    def test_message_claimant_permission_denied(self):
        self.client.login(username='user', password='userpass')

        response = self.__post_message_claimant(
            self.facility_claim.id, "Hello, claimant!"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.',
        )

    def test_message_claimant_not_found(self):
        self.__login_superuser()
        not_exist_id = 9999

        response = self.__post_message_claimant(
            not_exist_id, "Hello, claimant!"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_message_claimant_no_message(self):
        self.__login_superuser()

        response = self.__post_message_claimant(self.facility_claim.id, "")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Message is required.')

    def test_message_claimant_success(self):
        self.__login_superuser()

        response = self.__post_message_claimant(
            self.facility_claim.id, "Hello, claimant!"
        )
        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=self.facility_claim
        ).count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'][0]['note'], 'Hello, claimant!')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(notes_count, 1)

    @override_switch("claim_a_facility", active=True)
    def test_update_valid_number_of_workers_in_claimed_facility(self):
        self.__login_contributor()
        self.facility_claim.status = FacilityClaim.APPROVED
        self.facility_claim.save()
        self.update_claim_data["facility_workers_count"] = "100-249"

        response = self.client.put(
            self.update_claim_url, self.update_claim_data
        )
        updated_claim = FacilityClaim.objects.get(pk=self.facility_claim.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_claim.facility_workers_count, "100-249")

    @override_switch("claim_a_facility", active=True)
    def test_update_invalid_number_of_workers_in_claimed_facility(self):
        self.__login_contributor()
        self.facility_claim.status = FacilityClaim.APPROVED
        self.facility_claim.save()
        self.update_claim_data["facility_workers_count"] = "invalid"

        response = self.client.put(
            self.update_claim_url, self.update_claim_data
        )
        updated_claim = FacilityClaim.objects.get(pk=self.facility_claim.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_claim.facility_workers_count, None)

    @override_switch("claim_a_facility", active=True)
    def test_update_empty_number_of_workers_in_claimed_facility(self):
        self.__login_contributor()
        self.facility_claim.status = FacilityClaim.APPROVED
        self.facility_claim.save()
        self.update_claim_data["facility_workers_count"] = ""

        response = self.client.put(
            self.update_claim_url, self.update_claim_data
        )
        updated_claim = FacilityClaim.objects.get(pk=self.facility_claim.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_claim.facility_workers_count, None)
