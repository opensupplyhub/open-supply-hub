from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class ClaimTaxonomyIndexingTest(APITestCase):
    """
    OSDEV-3430: index_facility_type / index_processing_type count
    extended fields attached to an APPROVED claim, so claim status
    changes must recompute the facility_type / processing_type columns
    of api_facilityindex. Before the fix, perform_facility_claim_indexing
    did not touch those columns: approving a claim did not surface its
    facility types in the search filters, and revoking one did not
    remove them.
    """

    def setUp(self):
        self.user = User.objects.create(email='claimant@example.com')
        self.user.set_password('example123')
        self.user.save()
        self.contributor = Contributor.objects.create(
            name='Claimant Contributor', admin=self.user
        )
        self.facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='list'
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='name',
            address='address',
            country_code='US',
            sector=['Apparel'],
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        self.facility = Facility.objects.create(
            name='name',
            address='address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )
        self.claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Person',
            job_title='Title',
            status=FacilityClaimStatuses.PENDING,
        )
        # Taxonomy fields attached to the claim, not to any list item —
        # visible to index_facility_type / index_processing_type only
        # while the claim is APPROVED.
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_claim=self.claim,
            field_name=ExtendedField.FACILITY_TYPE,
            value={
                'raw_values': 'final product assembly',
                'matched_values': [
                    ['PROCESSING_TYPE', 'EXACT', 'Final Product Assembly',
                     'Final Product Assembly'],
                ],
            },
        )
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_claim=self.claim,
            field_name=ExtendedField.PROCESSING_TYPE,
            value={
                'raw_values': 'packaging',
                'matched_values': [
                    ['PROCESSING_TYPE', 'EXACT', 'Final Product Assembly',
                     'Packaging'],
                ],
            },
        )

    def index_row(self):
        return FacilityIndex.objects.get(id=self.facility.id)

    def set_claim_status(self, status):
        self.claim.status = status
        self.claim.save()

    def test_pending_claim_fields_are_not_indexed(self):
        self.assertEqual([], self.index_row().facility_type)
        self.assertEqual([], self.index_row().processing_type)

    def test_claim_approval_populates_taxonomy_columns(self):
        self.set_claim_status(FacilityClaimStatuses.APPROVED)
        self.assertIn('Final Product Assembly', self.index_row().facility_type)
        self.assertIn('Packaging', self.index_row().processing_type)

    def test_claim_revocation_clears_taxonomy_columns(self):
        self.set_claim_status(FacilityClaimStatuses.APPROVED)
        self.assertNotEqual([], self.index_row().facility_type)

        self.set_claim_status(FacilityClaimStatuses.REVOKED)
        self.assertEqual([], self.index_row().facility_type)
        self.assertEqual([], self.index_row().processing_type)
