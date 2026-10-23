from rest_framework import serializers

from api.models.facility.facility_claim_invite import FacilityClaimInvite


class FacilityClaimInviteSerializer(serializers.Serializer):
    '''
    Body of POST /api/facilities/{id}/claim-invite/: who to invite to
    claim the production location and an optional plain-text note from
    the sender.
    '''
    recipient_email = serializers.EmailField(
        required=True,
        allow_blank=False,
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        trim_whitespace=True,
        max_length=FacilityClaimInvite._meta.get_field('note').max_length,
    )

    def validate_recipient_email(self, value):
        return value.strip().lower()
