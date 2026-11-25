from rest_framework.serializers import SerializerMethodField

from ...services.facility_claim_status_service import get_status_label
from .facility_claim_review_note_serializer import note_is_automated
from .facility_claim_serializer import FacilityClaimSerializer


class FacilityClaimDashboardSerializer(FacilityClaimSerializer):
    """
    The moderator-dashboard claims list (claims dashboard v2 queue,
    OSDEV-3356): the base list serializer plus notes_meta — just enough
    of the note timeline (type + timestamp, no bodies) to derive queue
    stages client-side — the claim's campaign code (`campaign_code`),
    and the fields that refine `status` (OSDEV-3795): `waiting_on`,
    `denial_type`, `ai_decision` and the `status_label` staff read. All
    of these are for moderators only.

    Deliberately separate from FacilityClaimSerializer, which also
    serves claimant-facing endpoints (GET /api/facilities/claimed/):
    moderator note metadata, campaign codes and the automation
    pipeline's decision must not reach claimants (an auto-attributed
    claim would reveal another brand's campaign).
    Callers listing many claims must prefetch facilityclaimreviewnote_set
    and select_related('campaign') or this becomes an N+1.
    """

    notes_meta = SerializerMethodField()
    campaign_code = SerializerMethodField()
    status_label = SerializerMethodField()

    class Meta(FacilityClaimSerializer.Meta):
        fields = FacilityClaimSerializer.Meta.fields + (
            'notes_meta',
            'campaign_code',
            'status_label',
            'waiting_on',
            'denial_type',
            'ai_decision',
        )

    def get_status_label(self, claim):
        return get_status_label(claim)

    def get_campaign_code(self, claim):
        return claim.campaign.code if claim.campaign_id else None

    def get_notes_meta(self, claim):
        # is_automated must match the detail payload's notes exactly
        # (shared note_is_automated helper): the queue rail derives
        # stages from this payload and the workspace from the other.
        # Callers must select_related('author') on the prefetch or this
        # is an N+1 per note.
        return [
            {
                'note_type': note.note_type,
                'created_at': note.created_at,
                'is_automated': note_is_automated(note),
            }
            for note in claim.facilityclaimreviewnote_set.all()
        ]
