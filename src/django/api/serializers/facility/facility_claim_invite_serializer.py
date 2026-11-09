import re

from rest_framework import serializers

from api.models.facility.facility_claim_invite import FacilityClaimInvite


# The note goes out in an OS Hub-branded email, so it must not carry
# links: a scheme ("https://"), "www.", an IP address or a bare domain
# such as "login.example.ai/verify", which most email clients turn into
# a link. Any dotted name ending in letters counts as a domain, so a note
# like "Example Co.Ltd" is refused too; the sender can add a space.
NOTE_LINK_PATTERN = re.compile(
    r'[a-z][a-z0-9+.-]*://'
    r'|\bwww\.'
    r'|\b\d{1,3}(?:\.\d{1,3}){3}\b'
    r'|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:[a-z]{2,63}|xn--[a-z0-9-]+)\b',
    re.IGNORECASE,
)
NOTE_LINK_MESSAGE = 'Please remove links and web addresses from the note.'


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

    def validate_note(self, value):
        if NOTE_LINK_PATTERN.search(value):
            raise serializers.ValidationError(NOTE_LINK_MESSAGE)
        return value
