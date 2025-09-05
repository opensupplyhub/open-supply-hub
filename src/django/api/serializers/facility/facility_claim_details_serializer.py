from api.constants import FacilityClaimStatuses
from api.models.facility.facility_index import FacilityIndex
from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)

from ...models import (
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityClaimAttachments
)
from ..user.user_profile_serializer import UserProfileSerializer
from .facility_index_serializer import FacilityIndexSerializer
from .facility_claim_attachments_serializer import (
    FacilityClaimAttachmentsSerializer
)
from .facility_claim_review_note_serializer import (
    FacilityClaimReviewNoteSerializer
)
from .utils import _get_parent_company


class FacilityClaimDetailsSerializer(ModelSerializer):
    contributor = SerializerMethodField()
    facility = SerializerMethodField()
    status_change = SerializerMethodField()
    notes = SerializerMethodField()
    facility_parent_company = SerializerMethodField()
    email = SerializerMethodField()
    attachments = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'created_at', 'updated_at', 'contact_person', 'email',
                  'company_name', 'website', 'facility_description', 'status',
                  'contributor', 'facility', 'status_change', 'notes',
                  'facility_parent_company', 'job_title', 'linkedin_profile',
                  'attachments', 'facility_website', 'sector',
                  'facility_workers_count', 'facility_name_native_language', 'claim_reason')

    def get_contributor(self, claim):
        return UserProfileSerializer(claim.contributor.admin).data

    def get_facility(self, claim):
        facility = FacilityIndex.objects.get(id=claim.facility.id)
        return FacilityIndexSerializer(facility).data

    def get_status_change(self, claim):
        if claim.status == FacilityClaimStatuses.PENDING:
            return {
                'status_change_by': None,
                'status_change_date': None,
                'status_change_reason': None,
            }

        return {
            'status_change_by': claim.status_change_by.email,
            'status_change_date': claim.status_change_date,
            'status_change_reason': claim.status_change_reason,
        }

    def get_notes(self, claim):
        notes = (
            FacilityClaimReviewNote
            .objects
            .filter(claim=claim)
            .order_by('id')
        )
        data = (
            FacilityClaimReviewNoteSerializer(notes, many=True)
            .data
        )
        return data

    def get_facility_parent_company(self, claim):
        return _get_parent_company(claim)

    def get_email(self, claim):
        return claim.contributor.admin.email

    def get_attachments(self, claim):
        attachments = FacilityClaimAttachments.objects.filter(claim=claim)
        serializer = FacilityClaimAttachmentsSerializer(attachments, many=True)
        return serializer.data
