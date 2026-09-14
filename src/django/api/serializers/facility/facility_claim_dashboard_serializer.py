from rest_framework.serializers import SerializerMethodField

from .facility_claim_serializer import FacilityClaimSerializer


class FacilityClaimDashboardSerializer(FacilityClaimSerializer):
    """
    The moderator-dashboard claims list (claims dashboard v2 queue,
    OSDEV-3356): the base list serializer plus notes_meta — just enough
    of the note timeline (type + timestamp, no bodies) to derive queue
    stages client-side.

    Deliberately separate from FacilityClaimSerializer, which also
    serves claimant-facing endpoints (GET /api/facilities/claimed/):
    moderator note metadata must not reach claimants. Callers listing
    many claims must prefetch facilityclaimreviewnote_set or this
    becomes an N+1.
    """

    notes_meta = SerializerMethodField()

    class Meta(FacilityClaimSerializer.Meta):
        fields = FacilityClaimSerializer.Meta.fields + ('notes_meta',)

    def get_notes_meta(self, claim):
        return [
            {'note_type': note.note_type, 'created_at': note.created_at}
            for note in claim.facilityclaimreviewnote_set.all()
        ]
