'''
The rules behind the fields that refine a FacilityClaim's status
(OSDEV-3795): who a pending claim is waiting on, why a denied claim was
closed, and what the claims automation pipeline decided.

`status` keeps its four values (PENDING, APPROVED, DENIED, REVOKED),
which the API, the frontend and the pipeline all read. These fields sit
next to it, and the label staff see is built from both.
'''
import json
from typing import Optional

from django.conf import settings

from api.constants import (
    FacilityClaimAIDecisions,
    FacilityClaimDenialTypes,
    FacilityClaimStatuses,
    FacilityClaimWaitingOn,
)
from api.exceptions import BadRequestException
from api.models.facility.facility_claim import FacilityClaim
from api.models.user import User

# The marker the pipeline puts before the JSON block in its review note.
# The claims dashboard reads the same block (automatedReviewUtils.js).
AUTOMATED_REVIEW_MARKER = '--- machine-readable, do not edit ---'
AUTOMATED_REVIEW_KIND = 'automated_review'
AUTOMATED_REVIEW_VERSION = 1

DENIAL_TYPES = tuple(value for value, _ in FacilityClaim.DENIAL_TYPE_CHOICES)

DENIED_LABELS = {
    FacilityClaimDenialTypes.NO_RESPONSE: 'Closed, no response',
    FacilityClaimDenialTypes.NOT_ELIGIBLE: 'Denied, not eligible',
}

DECIDED_LABELS = {
    FacilityClaimStatuses.APPROVED: 'Approved',
    FacilityClaimStatuses.DENIED: 'Denied',
    FacilityClaimStatuses.REVOKED: 'Revoked',
}


def is_claims_automation_account(user: User) -> bool:
    '''
    True when the user is the account the claims automation pipeline
    acts as.

    Compared case-insensitively: User.save() lowercases emails on
    write, so a mixed-case setting value would otherwise never match.
    An empty setting means no account is the automation account.
    '''
    configured = (
        settings.CLAIMS_AUTOMATION_ACCOUNT_EMAIL or ''
    ).strip().lower()
    if not configured:
        return False
    return user.email.lower() == configured


def get_status_label(claim: FacilityClaim) -> str:
    '''The status as staff read it.'''
    if claim.status == FacilityClaimStatuses.PENDING:
        if claim.waiting_on == FacilityClaimWaitingOn.CLAIMANT:
            return 'Waiting on claimant'
        return 'Waiting on OS Hub'
    if claim.status == FacilityClaimStatuses.DENIED:
        return DENIED_LABELS.get(
            claim.denial_type,
            DECIDED_LABELS[FacilityClaimStatuses.DENIED],
        )
    return DECIDED_LABELS.get(claim.status, claim.status)


def mark_waiting_on_claimant(claim: FacilityClaim) -> None:
    '''
    The claimant was asked for something. Only a PENDING claim waits on
    anyone, so a message sent after the decision changes nothing.

    Saves `waiting_on` alone: messaging a claimant has never bumped the
    claim's `updated_at`, and still does not.
    '''
    if claim.status != FacilityClaimStatuses.PENDING:
        return
    if claim.waiting_on == FacilityClaimWaitingOn.CLAIMANT:
        return
    claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT
    claim.save(update_fields=['waiting_on'])


def resolve_denial_type(
    user: User,
    requested: Optional[str],
) -> Optional[str]:
    '''
    The denial type for a claim `user` is denying.

    A type sent with the request wins. Without one, a denial by the
    automation account is NO_RESPONSE: the pipeline only denies claims
    whose claimant never answered. A moderator's denial without a type
    stays unclassified rather than being guessed.
    '''
    if requested:
        if requested not in DENIAL_TYPES:
            raise BadRequestException(
                'denial_type must be one of: {}.'.format(
                    ', '.join(DENIAL_TYPES)
                )
            )
        return requested
    if is_claims_automation_account(user):
        return FacilityClaimDenialTypes.NO_RESPONSE
    return None


def _parse_automated_review(note: str) -> Optional[dict]:
    if not isinstance(note, str):
        return None
    marker_index = note.find(AUTOMATED_REVIEW_MARKER)
    if marker_index == -1:
        return None
    json_start = note.find('{', marker_index)
    if json_start == -1:
        return None
    try:
        review = json.loads(note[json_start:])
    except ValueError:
        return None
    if not isinstance(review, dict):
        return None
    if (review.get('v') != AUTOMATED_REVIEW_VERSION
            or review.get('kind') != AUTOMATED_REVIEW_KIND):
        return None
    return review


def _describe_automated_review(review: dict) -> str:
    lines = ['Automated review result: {}.'.format(review.get('decision'))]
    reasoning = review.get('reasoning')
    if isinstance(reasoning, dict):
        lines.extend(
            '{}: {}'.format(criterion, explanation)
            for criterion, explanation in reasoning.items()
        )
    return '\n'.join(lines)


def record_ai_review(claim: FacilityClaim, user: User, note: str) -> None:
    '''
    Record that the pipeline reviewed a claim and left it for a
    moderator, with its reasons.

    Called for every internal note. It only acts on the pipeline's own
    review note on a PENDING claim: that note carries the review as a
    JSON block after AUTOMATED_REVIEW_MARKER. A note without a block we
    understand is ignored, so posting the note never fails here. If the
    pipeline goes on to approve the claim, record_ai_approval replaces
    HELD with APPROVED.
    '''
    if claim.status != FacilityClaimStatuses.PENDING:
        return
    if not is_claims_automation_account(user):
        return
    review = _parse_automated_review(note)
    if review is None:
        return
    claim.ai_decision = FacilityClaimAIDecisions.HELD
    claim.ai_decision_reason = _describe_automated_review(review)
    claim.save(update_fields=['ai_decision', 'ai_decision_reason'])


def record_ai_approval(claim: FacilityClaim, user: User) -> None:
    '''
    Mark a claim the pipeline is approving. Sets the fields only; the
    caller saves the claim with the rest of the approval. The reason
    recorded with the pipeline's review is kept unless the approval
    request gave its own.
    '''
    if not is_claims_automation_account(user):
        return
    claim.ai_decision = FacilityClaimAIDecisions.APPROVED
    if claim.status_change_reason:
        claim.ai_decision_reason = claim.status_change_reason
