import json

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
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


class ApprovedFacilityClaimTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.user_contributor = Contributor.objects.create(
            admin=self.user,
            name="text contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contributor_email = "contributor@example.com"
        self.contributor_user = User.objects.create(
            email=self.contributor_email
        )

        self.list_contributor = Contributor.objects.create(
            admin=self.contributor_user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility_list = FacilityList.objects.create(
            header="header", file_name="one", name="List"
        )

        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.list_contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
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

        self.facility_match = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item,
        )

        self.facility_claim = FacilityClaim.objects.create(
            contributor=self.user_contributor,
            facility=self.facility,
            contact_person="Name",
            facility_phone_number='12345',
            company_name="Test",
            website="http://example.com",
            facility_description="description",
        )

        self.superuser_email = "superuser@example.com"
        self.superuser_password = "superuser"

        self.superuser = User.objects.create_superuser(
            self.superuser_email, self.superuser_password
        )

        self.client.login(email=self.email, password=self.password)

    @override_switch("claim_a_facility", active=True)
    def test_non_approved_facility_claim_is_not_visible(self):
        api_url = "/api/facility-claims/{}/claimed/".format(
            self.facility_claim.id
        )
        pending_response = self.client.get(api_url)
        self.assertEqual(404, pending_response.status_code)

        self.facility_claim.status = FacilityClaimStatuses.DENIED
        self.facility_claim.save()
        denied_response = self.client.get(api_url)
        self.assertEqual(404, denied_response.status_code)

        self.facility_claim.status = FacilityClaimStatuses.REVOKED
        self.facility_claim.save()
        revoked_response = self.client.get(api_url)
        self.assertEqual(404, revoked_response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_approved_facility_claim_is_visible_to_claimant(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response = self.client.get(
            "/api/facility-claims/{}/claimed/".format(self.facility_claim.id)
        )
        self.assertEqual(200, response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_other_user_approved_facility_claims_are_not_visible(self):
        self.client.logout()

        self.client.login(
            email=self.superuser_email, pasword=self.superuser_password
        )

        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response = self.client.get(
            "/api/facility-claims/{}/claimed/".format(self.facility_claim.id)
        )
        self.assertEqual(401, response.status_code)

    @override_switch("claim_a_facility", active=True)
    def test_approved_facility_claim_info_is_in_details_response(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.facility_description = "new_description"
        self.facility_claim.save()

        response_data = self.client.get(
            "/api/facilities/{}/".format(self.facility_claim.facility.id)
        ).json()["properties"]["claim_info"]["facility"]

        self.assertEqual(response_data["description"], "new_description")

    @override_switch("claim_a_facility", active=True)
    def test_updating_claim_profile_sends_email_to_contributor(self):
        self.assertEqual(len(mail.outbox), 0)
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response = self.client.put(
            "/api/facility-claims/{}/claimed/".format(self.facility_claim.id),
            {
                "facility_description": "test_facility_description",
                "facility_phone_number_publicly_visible": False,
                "point_of_contact_publicly_visible": False,
                "office_info_publicly_visible": False,
                "facility_website_publicly_visible": False,
            },
        )

        self.assertEqual(200, response.status_code)

        updated_description = FacilityClaim.objects.get(
            pk=self.facility_claim.id
        ).facility_description

        self.assertEqual(updated_description, "test_facility_description")

        self.assertEqual(len(mail.outbox), 1)

    @override_switch("claim_a_facility", active=True)
    def test_non_visible_facility_phone_is_not_in_details_response(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response_data = self.client.get(
            "/api/facilities/{}/".format(self.facility_claim.facility.id)
        ).json()["properties"]["claim_info"]["facility"]

        self.assertIsNone(response_data["phone_number"])

    @override_switch("claim_a_facility", active=True)
    def test_non_visible_office_info_is_not_in_details_response(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response_data = self.client.get(
            "/api/facilities/{}/".format(self.facility_claim.facility.id)
        ).json()["properties"]["claim_info"]

        self.assertIsNone(response_data["contact"])

    @override_switch("claim_a_facility", active=True)
    def test_non_visible_contact_info_is_not_in_details_response(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response_data = self.client.get(
            "/api/facilities/{}/".format(self.facility_claim.facility.id)
        ).json()["properties"]["claim_info"]

        self.assertIsNone(response_data["office"])

    @override_switch("claim_a_facility", active=True)
    def test_non_visible_website_is_not_in_details_response(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        response_data = self.client.get(
            "/api/facilities/{}/".format(self.facility_claim.facility.id)
        ).json()["properties"]["claim_info"]["facility"]

        self.assertIsNone(response_data["website"])

    @override_switch("claim_a_facility", active=True)
    def test_update_location(self):
        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.save()

        new_point = {"type": "Point", "coordinates": [44, 55]}
        response = self.client.put(
            "/api/facility-claims/{}/claimed/".format(self.facility_claim.id),
            {
                "facility_description": "test_facility_description",
                "facility_phone_number_publicly_visible": False,
                "point_of_contact_publicly_visible": False,
                "office_info_publicly_visible": False,
                "facility_website_publicly_visible": False,
                "facility_location": new_point,
                "facility_address": "134 Claim St",
            },
            format="json",
        )

        self.assertEqual(200, response.status_code)

        updated_location = FacilityClaim.objects.get(
            pk=self.facility_claim.id
        ).facility_location

        self.assertEqual(json.loads(updated_location.geojson), new_point)

    @override_switch("claim_a_facility", active=True)
    def test_clears_location(self):
        point = Point(44, 55)

        self.facility_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_claim.facility_address = "134 Claim St"
        self.facility_claim.facility_location = point
        self.facility_claim.save()

        original_facility_location = self.facility.location

        self.facility.location = point
        self.facility.save()

        self.client.put(
            "/api/facility-claims/{}/claimed/".format(self.facility_claim.id),
            {
                "facility_description": "test_facility_description",
                "facility_phone_number_publicly_visible": False,
                "point_of_contact_publicly_visible": False,
                "office_info_publicly_visible": False,
                "facility_website_publicly_visible": False,
                "facility_location": json.loads(point.geojson),
                "facility_address": "",
            },
            format="json",
        )

        updated_location = FacilityClaim.objects.get(
            pk=self.facility_claim.id
        ).facility_location
        self.assertIsNone(updated_location)

        updated_facility_location = Facility.objects.get(
            pk=self.facility_claim.facility_id
        ).location
        self.assertEqual(
            json.loads(updated_facility_location.geojson),
            json.loads(original_facility_location.geojson),
        )
