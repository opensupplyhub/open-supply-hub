from rest_framework.test import APITestCase
from django.db.models.signals import post_delete
from django.contrib.gis.geos import Point

from api.constants import ProcessingAction, FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityAlias,
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.signals import location_post_delete_handler_for_opensearch


class FacilityDeleteTest(APITestCase):
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

        self.other_user_email = "other@example.com"
        self.other_user_password = "other123"
        self.other_user = User.objects.create(email=self.other_user_email)
        self.other_user.set_password(self.other_user_password)
        self.other_user.save()

        self.superuser_email = "super@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.other_contributor = Contributor.objects.create(
            admin=self.other_user,
            name="other contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
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
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source_uuid=self.source,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )
        self.facility_url = "/api/facilities/{}/".format(self.facility.id)

        self.list_item.facility = self.facility
        self.list_item.save()

        self.facility_match = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item,
        )

    def test_requires_auth(self):
        response = self.client.delete(self.facility_url)
        self.assertEqual(401, response.status_code)

    def test_requires_superuser(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.delete(self.facility_url)
        self.assertEqual(403, response.status_code)

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

    def test_delete(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(
            0, Facility.objects.filter(id=self.facility.id).count()
        )
        self.assertEqual(
            0, FacilityMatch.objects.filter(facility=self.facility).count()
        )

        self.list_item.refresh_from_db()
        self.assertEqual(FacilityListItem.DELETED, self.list_item.status)
        self.assertEqual(
            ProcessingAction.DELETE_FACILITY,
            self.list_item.processing_results[-1]["action"],
        )
        self.assertEqual(
            self.facility.id,
            self.list_item.processing_results[-1]["deleted_os_id"],
        )

    def test_cant_delete_if_there_is_an_approved_claim(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="test",
            status=FacilityClaimStatuses.APPROVED,
        )
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(400, response.status_code)

    def test_unapproved_claims_are_deleted(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="test",
            status=FacilityClaimStatuses.PENDING,
        )
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)
        self.assertEqual(
            0, FacilityClaim.objects.filter(facility=self.facility).count()
        )

    def test_other_match_is_promoted(self):
        initial_facility_count = Facility.objects.all().count()
        list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(1, 1),
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source=source_2,
            source_uuid=source_2,
        )

        match_2 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_2,
            confidence=0.65,
            results="",
        )

        list_3 = FacilityList.objects.create(
            header="header", file_name="three", name="Third List"
        )

        source_3 = Source.objects.create(
            facility_list=list_3,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )

        list_item_3 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(2, 2),
            source=source_3,
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source_uuid=source_3,
        )

        match_3 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_3,
            confidence=0.85,
            results="",
        )

        alias = FacilityAlias.objects.create(
            facility=self.facility, os_id="US1234567ABCDEF"
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        # We should have "promoted" the matched facility to replace the deleted
        # facility
        facility_count = Facility.objects.all().count()
        self.assertEqual(facility_count, initial_facility_count)
        self.assertEqual(2, FacilityAlias.objects.all().count())

        # We should have created a new alias
        new_alias = FacilityAlias.objects.exclude(
            os_id="US1234567ABCDEF"
        ).first()
        self.assertEqual(FacilityAlias.DELETE, new_alias.reason)
        self.assertEqual(self.facility.id, new_alias.os_id)

        # The line item previously matched to the deleted facility should now
        # be matched to a new facility
        match_3.refresh_from_db()
        list_item_2.refresh_from_db()
        self.assertEqual(match_3.facility, list_item_2.facility)
        match_2.refresh_from_db()
        self.assertEqual(match_3.facility, match_2.facility)

        # We should have replaced the alias with one pointing to the new
        # facility
        alias.refresh_from_db()
        self.assertEqual(match_3.facility, alias.facility)

    def test_match_from_other_contributor_is_promoted(self):
        initial_facility_count = Facility.objects.all().count()
        list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(1, 1),
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source=source_2,
            source_uuid=source_2,
        )

        match_2 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_2,
            confidence=0.65,
            results="",
        )

        list_3 = FacilityList.objects.create(
            header="header", file_name="three", name="Third List"
        )

        source_3 = Source.objects.create(
            facility_list=list_3,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )

        list_item_3 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(2, 2),
            source=source_3,
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source_uuid=source_3,
        )

        match_3 = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_3,
            confidence=0.85,
            results="",
        )

        alias = FacilityAlias.objects.create(
            facility=self.facility, os_id="US1234567ABCDEF"
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        # The original facility should be deleted and have no matches
        self.assertEqual(
            0, FacilityMatch.objects.filter(facility=self.facility).count()
        )
        self.assertEqual(
            0, Facility.objects.filter(id=self.facility.id).count()
        )

        # We should have "promoted" the other contributor's
        # matched facility to replace the deleted facility
        facility_count = Facility.objects.all().count()
        self.assertEqual(facility_count, initial_facility_count)
        self.assertEqual(2, FacilityAlias.objects.all().count())

        # match 2 should be deleted because it's from the
        # deleted facility's contributor
        list_item_2.refresh_from_db()
        self.assertEqual(FacilityListItem.DELETED, list_item_2.status)
        self.assertEqual(
            0, FacilityMatch.objects.filter(id=match_2.id).count()
        )

        # We should have created a new alias
        new_alias = FacilityAlias.objects.exclude(
            os_id="US1234567ABCDEF"
        ).first()
        self.assertEqual(FacilityAlias.DELETE, new_alias.reason)
        self.assertEqual(self.facility.id, new_alias.os_id)

        # We should have replaced the alias with one pointing to the new
        # facility
        match_3.refresh_from_db()
        alias.refresh_from_db()
        self.assertEqual(match_3.facility, alias.facility)

    def test_matches_without_locations_are_ignored(self):
        list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=None,
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source=source_2,
            source_uuid=source_2,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_2,
            confidence=0.65,
            results="",
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(
            0, Facility.objects.filter(id=self.facility.id).count()
        )
        self.assertEqual(
            0, FacilityMatch.objects.filter(facility=self.facility).count()
        )

        self.list_item.refresh_from_db()
        self.assertEqual(FacilityListItem.DELETED, self.list_item.status)
        self.assertEqual(
            ProcessingAction.DELETE_FACILITY,
            self.list_item.processing_results[-1]["action"],
        )
        self.assertEqual(
            self.facility.id,
            self.list_item.processing_results[-1]["deleted_os_id"],
        )

    def test_other_inactive_match_is_promoted(self):
        initial_facility_count = Facility.objects.all().count()
        list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(1, 1),
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source=source_2,
            source_uuid=source_2,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_2,
            confidence=0.65,
            results="",
            is_active=False,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        # We should have "promoted" the matched facility to replace the deleted
        # facility
        facility_count = Facility.objects.all().count()
        self.assertEqual(facility_count, initial_facility_count)
        self.assertEqual(1, FacilityAlias.objects.all().count())
        alias = FacilityAlias.objects.first()
        self.assertEqual(list_item_2, alias.facility.created_from)

    def test_other_matches_from_same_contributor_are_deleted(self):
        initial_facility_count = Facility.objects.all().count()
        list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(1, 1),
            row_index=1,
            status=FacilityListItem.MATCHED,
            facility=self.facility,
            source=source_2,
            source_uuid=source_2,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_2,
            confidence=0.65,
            results="",
            is_active=False,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        # The facility should be deleted and not be replaced
        # since both items/matches came from the same contributor.
        facility_count = Facility.objects.all().count()
        self.assertEqual(facility_count, initial_facility_count - 1)
        self.assertEqual(0, FacilityAlias.objects.all().count())

    def test_rejected_match_is_deleted_not_promoted(self):
        list_2 = FacilityList.objects.create(
            header="header", file_name="one", name="Second List"
        )

        source_2 = Source.objects.create(
            facility_list=list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        list_item_2 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            geocoded_point=Point(1, 1),
            row_index=1,
            status=FacilityListItem.MATCHED,
            source=source_2,
            source_uuid=source_2,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.REJECTED,
            facility_list_item=list_item_2,
            confidence=0,
            facility=self.facility,
            results="",
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(0, Facility.objects.all().count())
        self.assertEqual(0, FacilityMatch.objects.all().count())
        self.assertEqual(0, FacilityAlias.objects.all().count())

        list_item_2.refresh_from_db()
        self.assertEqual(FacilityListItem.DELETED, list_item_2.status)
        self.assertIsNone(list_item_2.facility)
        self.assertEqual(
            ProcessingAction.DELETE_FACILITY,
            list_item_2.processing_results[-1]["action"],
        )

    def test_delete_with_alias(self):
        FacilityAlias.objects.create(
            facility=self.facility, os_id="US1234567ABCDEF"
        )
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

    def test_delete_removed_item(self):
        self.facility_match.is_active = False
        self.facility_match.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(
            0, Facility.objects.filter(id=self.facility.id).count()
        )
        self.assertEqual(
            0, FacilityMatch.objects.filter(facility=self.facility).count()
        )

    def test_can_delete_multiple_created_froms(self):
        FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.facility,
            facility_list_item=self.facility.created_from,
            confidence=0.85,
            results="",
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(
            0, Facility.objects.filter(id=self.facility.id).count()
        )
        self.assertEqual(
            0, FacilityMatch.objects.filter(facility=self.facility).count()
        )

    def test_can_delete_with_claim_notes(self):
        claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="test",
            status=FacilityClaimStatuses.DENIED,
        )

        FacilityClaimReviewNote.objects.create(
            claim=claim,
            author=self.user,
            note='Test',
        )

        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password
        )
        response = self.client.delete(self.facility_url)
        self.assertEqual(204, response.status_code)
        self.assertEqual(
            0, FacilityClaim.objects.filter(facility=self.facility).count()
        )
        self.assertEqual(
            0, FacilityClaimReviewNote.objects.filter(claim=claim).count()
        )
