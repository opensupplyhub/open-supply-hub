import json

from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.db.models.signals import post_delete

from api.constants import ProcessingAction, FacilityClaimStatuses
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityAlias,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.signals import location_post_delete_handler_for_opensearch


class FacilityMergeTest(APITestCase):
    def setUp(self):
        # Disconnect location deletion propagation to OpenSearch cluster, as
        # it is outside the scope of Django unit testing.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch,
            Facility
        )

        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.superuser_email = "super@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.api_user_email = "api@example.com"
        self.api_user_password = "example123"
        self.api_user = User.objects.create(email=self.api_user_email)
        self.api_user.set_password(self.api_user_password)
        self.api_user.save()

        self.contributor_1 = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_1 = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
        )

        self.source_1 = Source.objects.create(
            facility_list=self.list_1,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_1,
        )

        self.list_item_1 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_1,
        )

        self.facility_1 = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_1,
        )

        self.match_1 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_1,
            facility_list_item=self.list_item_1,
            confidence=0.85,
            results="",
        )

        self.list_item_1.facility = self.facility_1
        self.list_item_1.save()

        self.facility_1_claim = FacilityClaim.objects.create(
            contributor=self.contributor_1,
            facility=self.facility_1,
            contact_person="test 1",
            job_title="test 1",
            company_name="test 1",
            facility_description="test 1",
            status=FacilityClaimStatuses.APPROVED,
        )

        self.contributor_2 = Contributor.objects.create(
            admin=self.superuser,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        self.source_2 = Source.objects.create(
            facility_list=self.list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_2,
        )

        self.list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_2,
        )

        self.facility_2 = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_2,
        )

        self.match_2 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_2,
            facility_list_item=self.list_item_2,
            confidence=0.85,
            results="",
        )

        self.list_item_2.facility = self.facility_2
        self.list_item_2.save()

        self.facility_2_claim = FacilityClaim.objects.create(
            contributor=self.contributor_2,
            facility=self.facility_2,
            contact_person="test 2",
            job_title="test 2",
            company_name="test 2",
            facility_description="test 2",
        )

        self.contributor_3 = Contributor.objects.create(
            admin=self.api_user,
            name="test contributor 3",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.source_3 = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=False,
            contributor=self.contributor_3,
        )

        self.list_item_3 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            facility=self.facility_2,
            source=self.source_3,
        )

        self.extended_field_1 = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name one",
            contributor=self.contributor_1,
            facility=self.facility_1,
            facility_list_item=self.list_item_1,
            is_verified=True,
        )

        self.extended_field_2 = ExtendedField.objects.create(
            field_name="native_language_name",
            value="name two",
            contributor=self.contributor_2,
            facility=self.facility_2,
            facility_list_item=self.list_item_2,
        )

        self.existing_alias = FacilityAlias.objects.create(
            facility=self.facility_2, os_id="US1234567ABCDEF"
        )

        self.merge_endpoint = "/api/facilities/merge/"
        self.merge_url = "{}?target={}&merge={}".format(
            self.merge_endpoint, self.facility_1.id, self.facility_2.id
        )

    def set_up_updated_at_field(self):
        """Helper method to set updated_at field older than now"""
        self.facility_1.updated_at = '2019-03-24 02:23:22.195 +0100'
        self.old_updated_at = self.facility_1.updated_at
        self.facility_1.save(update_fields=['updated_at'])

    def test_requires_auth(self):
        response = self.client.post(self.merge_url)
        self.assertEqual(401, response.status_code)

    def test_requires_superuser(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.post(self.merge_url)
        self.assertEqual(403, response.status_code)

    def test_merge(self):
        current_time = timezone.now()
        self.set_up_updated_at_field()
        original_facility_count = Facility.objects.all().count()
        original_alias_count = FacilityAlias.objects.all().count()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_url)
        self.assertNotEqual(self.old_updated_at, self.facility_1.updated_at)
        self.assertEqual(
            current_time.replace(microsecond=0),
            self.facility_1.updated_at.replace(microsecond=0))
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(self.facility_1.id, data["id"])
        self.assertEqual(
            original_facility_count - 1, Facility.objects.all().count()
        )

        # The target models should not have changed
        self.list_item_1.refresh_from_db()
        self.assertEqual(self.list_item_1.facility, self.facility_1)
        self.match_1.refresh_from_db()
        self.assertEqual(self.match_1.facility, self.facility_1)
        self.assertEqual(self.match_1.facility_list_item, self.list_item_1)

        self.list_item_2.refresh_from_db()
        self.assertEqual(self.list_item_2.facility, self.facility_1)
        self.match_2.refresh_from_db()
        self.assertEqual(self.match_2.facility, self.facility_1)
        self.assertEqual(self.match_2.facility_list_item, self.list_item_2)
        self.assertEqual(
            ProcessingAction.MERGE_FACILITY,
            self.list_item_2.processing_results[-1]["action"],
        )

        self.facility_1.refresh_from_db()
        self.assertIn(self.source_1, self.facility_1.sources())
        self.assertIn(self.source_2, self.facility_1.sources())

        self.assertEqual(
            original_alias_count + 1, FacilityAlias.objects.all().count()
        )
        alias = FacilityAlias.objects.first()
        for alias in FacilityAlias.objects.all():
            self.assertEqual(self.facility_1, alias.facility)
            self.assertIn(
                alias.os_id, (self.facility_2.id, self.existing_alias.os_id)
            )
            self.assertEqual(FacilityAlias.MERGE, alias.reason)

        self.facility_2_claim.refresh_from_db()
        # The pending claim on the merge facility should have been updated
        self.assertEqual(self.facility_1, self.facility_2_claim.facility)
        self.assertEqual(
            FacilityClaimStatuses.DENIED,
            self.facility_2_claim.status
        )

    def test_merge_with_extended_fields(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_url)
        self.assertEqual(200, response.status_code)

        # Fields pointing to target facility should be unchanged
        self.extended_field_1.refresh_from_db()
        self.assertEqual(self.extended_field_1.facility, self.facility_1)
        self.assertEqual(
            self.extended_field_1.facility_list_item, self.list_item_1
        )

        # Fields pointing to merge facility should be updated
        self.extended_field_2.refresh_from_db()
        self.assertEqual(self.extended_field_2.facility, self.facility_1)
        self.assertEqual(
            self.extended_field_2.facility_list_item, self.list_item_2
        )

    def test_updates_facility_index(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_url)
        self.assertEqual(200, response.status_code)

        facility_index = FacilityIndex.objects.get(id=self.facility_1.id)
        self.assertIn(
            self.extended_field_1.value, facility_index.native_language_name
        )
        self.assertIn(
            self.extended_field_2.value, facility_index.native_language_name
        )

    def test_merge_with_two_approved_claims(self):
        self.facility_1_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_1_claim.save()
        self.facility_2_claim.status = FacilityClaimStatuses.APPROVED
        self.facility_2_claim.save()

        just_before_change = timezone.now()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_url)
        self.assertEqual(200, response.status_code)

        self.facility_1_claim.refresh_from_db()
        self.facility_2_claim.refresh_from_db()

        self.assertEqual(self.facility_1, self.facility_2_claim.facility)
        self.assertEqual(
            FacilityClaimStatuses.APPROVED,
            self.facility_1_claim.status
        )
        self.assertEqual(
            FacilityClaimStatuses.REVOKED,
            self.facility_2_claim.status
        )
        self.assertEqual(
            self.superuser, self.facility_2_claim.status_change_by
        )
        self.assertGreater(
            self.facility_2_claim.status_change_date, just_before_change
        )

    def test_required_params(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_endpoint)
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("target", data)
        self.assertIn("merge", data)

    def test_params_reference_existing_objects(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        url = "{}?target={}&merge={}".format(self.merge_endpoint, "foo", "bar")
        response = self.client.post(url)
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("target", data)
        self.assertIn("merge", data)

    def test_requires_distinct_params(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.post(self.merge_url)
        self.assertEqual(403, response.status_code)

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        url = "{}?target={}&merge={}".format(
            self.merge_endpoint, self.facility_1.id, self.facility_1.id
        )
        response = self.client.post(url)
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("target", data)
        self.assertIn("merge", data)

    def test_merge_handles_rejected_matches(self):
        list_item_3 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_3,
        )

        facility_3 = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=list_item_3,
        )

        match_3 = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=facility_3,
            facility_list_item=list_item_3,
            confidence=0.85,
            results="",
        )

        list_item_3.facility = facility_3
        list_item_3.save()

        match_4 = FacilityMatch.objects.create(
            status=FacilityMatch.REJECTED,
            facility=self.facility_2,
            facility_list_item=list_item_3,
            confidence=0.85,
            results="",
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.merge_url)
        self.assertEqual(200, response.status_code)

        list_item_3.refresh_from_db()
        match_3.refresh_from_db()
        match_4.refresh_from_db()

        self.assertEqual(facility_3, list_item_3.facility)
        self.assertEqual(facility_3, match_3.facility)
        self.assertEqual(self.facility_1, match_4.facility)
        self.assertEqual(FacilityMatch.REJECTED, match_4.status)
