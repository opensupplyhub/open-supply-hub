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

        self.client.login(email="superuser@example.com", password="superuser")

    def _post_message_claimant(self, claim_id, message):
        return self.client.post(
            "/api/facility-claims/{}/message-claimant/".format(claim_id),
            {"message": message},
        )

    def test_message_claimant_permission_denied(self):
        self.client.logout()
        self.client.login(username='user', password='userpass')

        response = self._post_message_claimant(
            self.facility_claim.id, "Hello, claimant!"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.',
        )

    def test_message_claimant_not_found(self):
        not_exist_id = 9999
        response = self._post_message_claimant(
            not_exist_id, "Hello, claimant!"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_message_claimant_no_message(self):
        response = self._post_message_claimant(self.facility_claim.id, "")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Message is required.')

    def test_message_claimant_success(self):
        response = self._post_message_claimant(
            self.facility_claim.id, "Hello, claimant!"
        )
        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=self.facility_claim
        ).count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'][0]['note'], 'Hello, claimant!')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(notes_count, 1)
