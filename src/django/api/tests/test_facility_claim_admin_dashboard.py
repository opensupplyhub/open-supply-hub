from django.utils import timezone
from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.core import mail


class FacilityClaimAdminDashboardTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

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

        self.list_item_first = FacilityListItem.objects.create(
            name="ItemFirst",
            address="AddressFirst",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            source_uuid=self.source,
        )

        self.list_item_second = FacilityListItem.objects.create(
            name="ItemSecond",
            address="AddressSecond",
            country_code="US",
            sector=["Apparel"],
            row_index=2,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            source_uuid=self.source,
        )

        self.facility_first = Facility.objects.create(
            name="NameFacilityFirst",
            address="AddressFirst",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_first,
        )

        self.facility_second = Facility.objects.create(
            name="NameFacilitySecond",
            address="AddressSecond",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_second,
        )

        self.facility_match = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility_first,
            results="",
            facility_list_item=self.list_item_first,
        )

        self.facility_claim_first = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility_first,
            contact_person="ContactPersonNameFirst",
            company_name="TestFirst",
            website="http://example_1.com",
            facility_description="description_1",
        )

        self.facility_claim_second = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility_second,
            contact_person="ContactPersonNameSecond",
            company_name="TestSecond",
            website="http://example_2.com",
            facility_description="description_2",
        )

        self.superuser = User.objects.create_superuser(
            "superuser@example.com", "superuser"
        )

        self.client.login(email="superuser@example.com", password="superuser")
        self.current_time = timezone.now()

    """Helper methods to set updated_at field older than now"""
    def set_up_first_updated_at_field(self):
        self.facility_first.updated_at = '2019-03-24 02:23:22.195 +0100'
        self.old_updated_at = self.facility_first.updated_at
        self.facility_first.save(update_fields=['updated_at'])

    def set_up_second_updated_at_field(self):
        self.facility_second.updated_at = '2019-03-24 02:23:22.195 +0100'
        self.old_updated_at = self.facility_second.updated_at
        self.facility_second.save(update_fields=['updated_at'])

    @override_switch("claim_a_facility", active=True)
    def test_user_cannot_submit_first_facility_claim_with_one_pending(self):
        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.post(
            "/api/facilities/{}/claim/".format(self.facility_first.id),
            {
                "your_name": "ClaimantName",
                "your_title": "Owner",
                "your_business_website":
                    "https://your-business-website.com",
                "business_linkedin_profile":
                    "https://www.linkedin.com/in/my-profile",
                "business_website": "https://www.business-website.com",
                "sectors": "Apparel",
                "number_of_workers": "15-30",
                "local_language_name": "LocalName",
            },
        )

        self.assertEqual(400, error_response.status_code)

        self.assertEqual(
            error_response.json()["detail"],
            "There is already a pending claim on this facility.",
        )

    @override_switch("claim_a_facility", active=True)
    def test_user_cannot_submit_second_facility_claim_with_one_approved(self):
        self.client.post(
            "/api/facility-claims/{}/approve/".format(
                self.facility_claim_second.id
            )
        )

        updated_facility_claim = FacilityClaim.objects.get(
            pk=self.facility_claim_second.id
        )

        self.assertEqual(
            FacilityClaimStatuses.APPROVED,
            updated_facility_claim.status,
        )

        self.set_up_second_updated_at_field()
        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.post(
            "/api/facilities/{}/claim/".format(self.facility_second.id),
            {
                "your_name": "ClaimantName",
                "your_title": "Owner",
                "your_business_website":
                    "https://www.your-business-website.com",
                "business_linkedin_profile":
                    "https://www.linkedin.com/in/my-profile",
                "business_website": "https://www.business-website.com",
                "sectors": "Apparel",
                "number_of_workers": "15-30",
                "local_language_name": "LocalName",
            },
        )

        self.assertEqual(400, error_response.status_code)

        self.assertEqual(
            error_response.json()["detail"],
            "There is already an approved claim on this facility.",
        )

    @override_switch("claim_a_facility", active=True)
    def test_user_cannot_submit_first_facility_without_your_name_field(self):
        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.post(
            "/api/facilities/{}/claim/".format(self.facility_first.id),
            {
                "your_title": "Owner",
                "your_business_website":
                    "https://www.your-business-website.com",
                "business_linkedin_profile":
                    "https://www.linkedin.com/in/my-profile",
                "business_website": "https://www.business-website.com",
                "sectors": "Apparel",
                "number_of_workers": "15-30",
                "local_language_name": "LocalName",
            },
        )

        self.assertEqual(400, error_response.status_code)

        self.assertEqual(
            error_response.json(),
            {
                "your_name": [
                    "This field is required."
                ]
            },
        )

    @override_switch("claim_a_facility", active=True)
    def test_user_cannot_submit_first_facility_without_your_title_field(self):
        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.post(
            "/api/facilities/{}/claim/".format(self.facility_first.id),
            {
                "your_name": "ClaimantName",
                "your_business_website":
                    "https://www.your-business-website.com",
                "business_linkedin_profile":
                    "https://www.linkedin.com/in/my-profile",
                "business_website": "https://www.business-website.com",
                "sectors": "Apparel",
                "number_of_workers": "15-30",
                "local_language_name": "LocalName",
            },
        )

        self.assertEqual(400, error_response.status_code)

        self.assertEqual(
            error_response.json(),
            {
                "your_title": [
                    "This field is required."
                ]
            },
        )

    @override_switch("claim_a_facility", active=True)
    def test_user_cannot_submit_first_facility_without_linkedin_field(self):
        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.post(
            "/api/facilities/{}/claim/".format(self.facility_first.id),
            {
                "your_name": "ClaimantName",
                "your_title": "Owner",
                "your_business_website":
                    "https://www.your-business-website.com",
                "business_website":
                    "https://www.business-website.com",
                "sectors": "Apparel",
                "number_of_workers": "15-30",
                "local_language_name": "LocalName",
            },
        )

        self.assertEqual(400, error_response.status_code)

        self.assertEqual(
            error_response.json(),
            {
                "business_linkedin_profile": [
                    "This field is required."
                ]
            },
        )

    @override_switch("claim_a_facility", active=True)
    def test_approve_claim_and_email_claimant_and_contributors(self):
        self.set_up_first_updated_at_field()

        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            "/api/facility-claims/{}/approve/".format(
                self.facility_claim_first.id
            )
        )
        self.assertEqual(
            self.current_time.replace(microsecond=0),
            self.facility_first.updated_at.replace(microsecond=0))
        self.assertNotEqual(
            self.old_updated_at,
            self.facility_first.updated_at
        )

        self.assertEqual(200, response.status_code)

        # Expect two emails to have been sent:
        #   - one to the user who submitted the facility claim
        #   - one to a contributor who has this facility on a list
        self.assertEqual(len(mail.outbox), 2)

        updated_facility_claim = FacilityClaim.objects.get(
            pk=self.facility_claim_first.id
        )

        self.assertEqual(
            FacilityClaimStatuses.APPROVED,
            updated_facility_claim.status,
        )

        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=updated_facility_claim
        ).count()

        self.assertEqual(notes_count, 1)

        error_response = self.client.post(
            "/api/facility-claims/{}/approve/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(400, error_response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_can_approve_at_most_one_facility_claim(self):
        response = self.client.post(
            "/api/facility-claims/{}/approve/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(200, response.status_code)

        updated_facility_claim = FacilityClaim.objects.get(
            pk=self.facility_claim_first.id
        )

        self.assertEqual(
            FacilityClaimStatuses.APPROVED,
            updated_facility_claim.status,
        )

        new_user = User.objects.create(email="new_user@example.com")
        new_contributor = Contributor.objects.create(
            admin=new_user,
            name="new_contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        new_facility_claim = FacilityClaim.objects.create(
            contributor=new_contributor,
            facility=self.facility_first,
            contact_person="ContactPersonName",
            company_name="CompanyName",
            website="http://example.com",
            facility_description="description",
        )

        error_response = self.client.post(
            "/api/facility-claims/{}/approve/".format(new_facility_claim.id)
        )

        self.assertEqual(400, error_response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_deny_facility_claim(self):
        self.set_up_first_updated_at_field()
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            "/api/facility-claims/{}/deny/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(
            self.current_time.replace(microsecond=0),
            self.facility_first.updated_at.replace(microsecond=0))
        self.assertNotEqual(
            self.old_updated_at,
            self.facility_first.updated_at
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(len(mail.outbox), 1)

        updated_facility_claim = FacilityClaim.objects.get(
            pk=self.facility_claim_first.id
        )

        self.assertEqual(
            FacilityClaimStatuses.DENIED,
            updated_facility_claim.status,
        )

        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=updated_facility_claim
        ).count()

        self.assertEqual(notes_count, 1)

        error_response = self.client.post(
            "/api/facility-claims/{}/deny/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(400, error_response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_revoke_facility_claim(self):
        self.set_up_first_updated_at_field()
        self.assertEqual(len(mail.outbox), 0)

        error_response = self.client.post(
            "/api/facility-claims/{}/revoke/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(400, error_response.status_code)

        self.facility_claim_first.status = FacilityClaimStatuses.APPROVED
        self.facility_claim_first.save()

        response = self.client.post(
            "/api/facility-claims/{}/revoke/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(len(mail.outbox), 1)

        updated_facility_claim = FacilityClaim.objects.get(
            pk=self.facility_claim_first.id
        )

        self.assertEqual(
            self.current_time.replace(microsecond=0),
            self.facility_first.updated_at.replace(microsecond=0))
        self.assertNotEqual(
            self.old_updated_at,
            self.facility_first.updated_at
        )

        self.assertEqual(
            FacilityClaimStatuses.REVOKED,
            updated_facility_claim.status,
        )

        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=updated_facility_claim
        ).count()

        self.assertEqual(notes_count, 1)

        another_error_response = self.client.post(
            "/api/facility-claims/{}/revoke/".format(
                self.facility_claim_first.id
            )
        )

        self.assertEqual(400, another_error_response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_add_claim_review_note(self):
        api_url = "/api/facility-claims/{}/note/".format(
            self.facility_claim_first.id
        )
        response = self.client.post(api_url, {"note": "note"})

        self.assertEqual(200, response.status_code)

        notes_count = FacilityClaimReviewNote.objects.filter(
            claim=self.facility_claim_first
        ).count()

        self.assertEqual(notes_count, 1)

    @override_switch("claim_a_facility", active=True)
    def test_claims_list_API_accessible_only_to_superusers(self):
        response = self.client.get("/api/facility-claims/")
        self.assertEqual(200, response.status_code)

        self.client.logout()
        self.client.login(email=self.email, password=self.password)

        error_response = self.client.get("/api/facility-claims/")
        self.assertEqual(403, error_response.status_code)
