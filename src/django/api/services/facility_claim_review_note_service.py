'''
The one place a FacilityClaimReviewNote is written.

Notes are created from several corners of the claim flow: the moderator
decisions (approve, deny, revoke) and the add-note action in the claim
view set, the claimant message and claimant update emails in mail.py, and
the contribution service when a claimed address could not move the pin.
Routing them through one function keeps the direction (note_type) an
explicit choice at every call site.
'''
from api.constants import FacilityClaimReviewNoteTypes
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_claim_review_note import (
    FacilityClaimReviewNote,
)
from api.models.user import User


def create_review_note(
    claim: FacilityClaim,
    author: User,
    note: str,
    note_type: str = FacilityClaimReviewNoteTypes.INTERNAL,
) -> FacilityClaimReviewNote:
    return FacilityClaimReviewNote.objects.create(
        claim=claim,
        author=author,
        note=note,
        note_type=note_type,
    )
