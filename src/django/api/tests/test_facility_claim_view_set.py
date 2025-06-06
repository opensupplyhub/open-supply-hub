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
        self.email_first = "test_first@example.com"
        self.email_second = 'test_second@example.com'
        self.password = "example123"
        self.user_first = User.objects.create(email=self.email_first)
        self.user_second = User.objects.create(email=self.email_second)
        self.user_first.set_password(self.password)
        self.user_second.set_password(self.password)
        self.user_first.save()
        self.user_second.save()

        self.superuser = User.objects.create_superuser(
            "superuser@example.com", "superuser"
        )

        self.contributor_first = Contributor.objects.create(
            admin=self.user_first,
            name="first test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contributor_second = Contributor.objects.create(
            admin=self.user_second,
            name="second test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_first = FacilityList.objects.create(
            header="header", file_name="one", name="List First"
        )

        self.list_second = FacilityList.objects.create(
            header="header", file_name="two", name="List Second"
        )

        self.source_first = Source.objects.create(
            facility_list=self.list_first,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_first,
        )

        self.source_second = Source.objects.create(
            facility_list=self.list_second,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_second,
        )

        self.list_item_first = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_first,
            source_uuid=self.source_first,
        )

        self.list_item_second = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="CN",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_second,
            source_uuid=self.source_second,
        )

        self.list_item_third = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="TR",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_second,
            source_uuid=self.source_second,
        )

        self.facility_first = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_first,
        )

        self.facility_second = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="CN",
            location=Point(0, 0),
            created_from=self.list_item_second,
        )

        self.facility_third = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="TR",
            location=Point(0, 0),
            created_from=self.list_item_third,
        )

        self.facility_claim_first = FacilityClaim.objects.create(
            contributor=self.contributor_first,
            facility=self.facility_first,
            contact_person="Name",
            company_name="Test",
            website="http://example.com",
            facility_description="description",
        )

        self.facility_claim_active = FacilityClaim.objects.create(
            contributor=self.contributor_second,
            facility=self.facility_second,
            contact_person="Name",
            company_name="Test",
            website="http://example.com",
            facility_description="active facility claim description",
            status='ACTIVE',
        )

        self.facility_claim_revoked = FacilityClaim.objects.create(
            contributor=self.contributor_second,
            facility=self.facility_third,
            contact_person="Name",
            company_name="Test",
            website="http://example.com",
            facility_description="first revoked facility claim description",
            status='REVOKED',
        )

        self.facility_claim_revoked_second = FacilityClaim.objects.create(
            contributor=self.contributor_second,
            facility=self.facility_third,
            contact_person="Name",
            company_name="Test",
            website="http://example.com",
            facility_description="second revoked facility claim description",
            status='REVOKED',
        )

        self.facility_claim_denied = FacilityClaim.objects.create(
            contributor=self.contributor_second,
            facility=self.facility_third,
            contact_person="Name",
            company_name="Test",
            website="http://example.com",
            facility_description="revoked facility claim description",
            status='DENIED',
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
            self.facility_claim_first.id, "Hello, claimant!"
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
        response = self._post_message_claimant(
            self.facility_claim_first.id, ""
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Message is required.')

    def test_message_claimant_success(self):
        response = self._post_message_claimant(
            self.facility_claim_first.id, "Hello, claimant!"
        )
        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=self.facility_claim_first
        ).count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'][0]['note'], 'Hello, claimant!')
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(notes_count, 1)

    def get_facility_claims(self, statuses='', countries=''):
        url = '/api/facility-claims/?' + statuses + countries
        return self.client.get(url)

    def test_all_claims(self):
        response = self.get_facility_claims()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            5,
            "Expected to receive all possible claims"
        )

    def test_single_claim_by_status(self):
        response = self.get_facility_claims(statuses='statuses=DENIED')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            1,
            "Expected one claim with status 'DENIED'"
        )

    def test_multiple_claims_by_status(self):
        response = self.get_facility_claims(
            statuses='statuses=REVOKED&statuses=DENIED'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            3,
            "Expected two claims with status 'REVOKED' \
            and one with status 'DENIED"
        )

    def test_single_claim_by_country(self):
        response = self.get_facility_claims(countries='countries=US')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            1,
            "Expected one claim for 'US' country"
        )

    def test_multiple_claims_by_country(self):
        response = self.get_facility_claims(
            countries='countries=TR&countries=CN'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            4,
            "Expected four claims for 'CN' and 'TR' countries"
        )

    def test_multiple_claims_by_status_and_country(self):
        response = self.get_facility_claims(
            statuses='statuses=PENDING&statuses=REVOKED',
            countries='&countries=US&countries=TR'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            3,
            "Expected three claims for 'US' and 'TR' \
            countries with statuses 'PENDING and 'REVOKED'"
        )
