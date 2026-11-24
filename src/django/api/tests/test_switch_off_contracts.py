"""The OFF side of feature switches is a contract too.

Reviewers caught several flag-gating bugs by hand last quarter (a form
writing real data with its switch off, a flag check present in one
layer and missing in another, an invalid flag value treated as the
permissive default). Tests routinely assert what a switch enables and
almost never what OFF must look like - waffle switches default inactive
under test, so the OFF path is exercised incidentally but its behavior
is pinned nowhere. These tests assert the OFF contract explicitly for
the widest-radius switches.

claim_a_facility's list() action is deliberately not asserted here:
today it is permission-gated but not switch-gated, unlike retrieve()
and the decision actions, and that asymmetry is tracked as its own
issue rather than pinned as a contract.
"""
from rest_framework import status
from waffle.testutils import override_switch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from api.constants import FacilityClaimStatuses
from api.models import FacilityClaim
from api.tests.claim_fixtures import make_claim
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


@override_switch("claim_a_facility", active=False)
class ClaimSwitchOffContractTest(FacilityAPITestCaseBase):
    """With claim_a_facility off, the gated claim actions are 404 and
    never move a claim's status."""

    def setUp(self):
        super().setUp()
        self.claim = make_claim(self.facility, self.contributor)
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

    def assert_claim_untouched(self):
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)

    def test_retrieve_is_not_found(self):
        response = self.client.get(f"/api/facility-claims/{self.claim.id}/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_approve_is_not_found_and_writes_nothing(self):
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/approve/"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assert_claim_untouched()

    def test_deny_is_not_found_and_writes_nothing(self):
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/deny/"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assert_claim_untouched()

    def test_revoke_is_not_found_and_writes_nothing(self):
        self.claim.status = FacilityClaimStatuses.APPROVED
        self.claim.save()
        response = self.client.post(
            f"/api/facility-claims/{self.claim.id}/revoke/"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.APPROVED, self.claim.status)

    def test_claim_submission_is_not_found_and_creates_nothing(self):
        previous_count = FacilityClaim.objects.count()
        response = self.client.post(
            f"/api/facilities/{self.facility.id}/claim/",
            {"contact_person": "P", "job_title": "T"},
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(previous_count, FacilityClaim.objects.count())


class ListUploadSwitchOffContractTest(FacilityAPITestCaseBase):
    """disable_list_uploading is a maintenance kill switch: only its ON
    path (uploads blocked, 503) is tested elsewhere. Pin the OFF
    contract - uploads work - so a switch stuck active, or a default
    flipped in a refactor, fails a test instead of silently stopping
    every contribution."""

    @override_switch("disable_list_uploading", active=False)
    def test_upload_works_with_the_kill_switch_off(self):
        self.client.login(email=self.user_email, password=self.user_password)
        csv_file = SimpleUploadedFile(
            "facilities.csv",
            b"country,name,address,sector\n"
            b"US,Somewhere,999 Park St,Apparel\n",
            content_type="text/csv",
        )
        response = self.client.post(
            reverse("facility-list-list"),
            {"file": csv_file},
            format="multipart",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code,
                         response.content)
