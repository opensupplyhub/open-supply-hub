from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)
from countries.lib.countries import COUNTRY_NAMES
from ...models import FacilityClaim


class FacilityClaimSerializer(ModelSerializer):
    facility_name = SerializerMethodField()
    os_id = SerializerMethodField()
    contributor_name = SerializerMethodField()
    contributor_id = SerializerMethodField()
    facility_address = SerializerMethodField()
    facility_country_name = SerializerMethodField()
    claim_decision = SerializerMethodField()
    notes_meta = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'created_at', 'updated_at', 'contributor_id', 'os_id',
                  'contributor_name', 'facility_name', 'facility_address',
                  'facility_country_name', 'status', 'claim_decision',
                  'notes_meta')

    def get_facility_name(self, claim):
        return claim.facility.name

    def get_os_id(self, claim):
        return claim.facility_id

    def get_contributor_name(self, claim):
        return claim.contributor.name

    def get_contributor_id(self, claim):
        return claim.contributor.admin.id

    def get_facility_address(self, claim):
        return claim.facility.address

    def get_facility_country_name(self, claim):
        return COUNTRY_NAMES.get(claim.facility.country_code, '')

    def get_claim_decision(self, claim):
        return claim.status_change_date

    def get_notes_meta(self, claim):
        # Just enough of the note timeline for the claims dashboard v2
        # queue to derive stages client-side (OSDEV-3356) without the
        # note bodies. Callers listing many claims must prefetch
        # facilityclaimreviewnote_set or this becomes an N+1.
        return [
            {'note_type': note.note_type, 'created_at': note.created_at}
            for note in claim.facilityclaimreviewnote_set.all()
        ]
