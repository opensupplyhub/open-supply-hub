from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListField,
    Serializer,
)


class FacilityClaimLiveCheckSerializer(Serializer):
    """
    What a claimant is told about the live check of their claim
    (OSDEV-3804): where it stands, the keys of the preset fixes when it
    did not pass, and how many checks the claim has left. Deliberately
    not a ModelSerializer over the claim: nothing the pipeline or a
    moderator wrote (scores, review notes, the AI decision and its
    reason) may reach the claimant through here.
    """

    status = CharField()
    fixes = ListField(child=CharField())
    checks_left = IntegerField()
