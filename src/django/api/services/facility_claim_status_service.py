'''
The rules behind the fields that refine a FacilityClaim's status
(OSDEV-3795): who a pending claim is waiting on, why a denied claim was
closed, and what the claims automation pipeline decided.

`status` keeps its four values (PENDING, APPROVED, DENIED, REVOKED),
which the API, the frontend and the pipeline all read. These fields sit
next to it, and the label staff see is built from both.
'''
import json
import logging
from datetime import datetime
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

log = logging.getLogger(__name__)

# The marker the pipeline puts before the JSON block in its review note.
# The claims dashboard reads the same block (parseBlock in
# automatedReviewUtils.js), and the two readers accept the same notes:
# the block is the last thing in the note, with only whitespace after
# it. Change them together.
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


def mark_waiting_on_claimant(
    claim: FacilityClaim,
    asked_at: Optional[datetime] = None,
) -> None:
    '''
    The claimant was asked for something. Only a PENDING claim waits on
    anyone, so a message sent after the decision changes nothing.

    `asked_at` is when the message was started. A claimant who updated
    the claim after that has the last move, so the claim stays waiting
    on OS Hub. It is the rule the 0288 backfill applies to old claims:
    a claim waits on the claimant only when they have not updated it
    since the message.

    Saves `waiting_on` alone: messaging a claimant has never bumped the
    claim's `updated_at`, and still does not.
    '''
    if claim.status != FacilityClaimStatuses.PENDING:
        return
    if claim.waiting_on == FacilityClaimWaitingOn.CLAIMANT:
        return
    if (asked_at is not None
            and claim.claimant_updated_at is not None
            and claim.claimant_updated_at > asked_at):
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

    Only a missing value and the empty string count as "no type sent".
    Anything else, including false, 0 or an empty list, is checked
    against the known types and refused.
    '''
    if requested is not None and requested != '':
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


def _read_review_block(note: str) -> Optional[dict]:
    '''
    The JSON object that follows the marker, or None when there is no
    object we understand. The object must be the last thing in the
    note: anything but whitespace after it makes the block unreadable,
    as it does for the dashboard, which parses everything from the
    first brace to the end of the note.
    '''
    json_start = note.find('{', note.find(AUTOMATED_REVIEW_MARKER))
    if json_start == -1:
        return None
    text = note[json_start:]
    try:
        review, end = json.JSONDecoder().raw_decode(text)
    except ValueError:
        return None
    if text[end:].strip() or not isinstance(review, dict):
        return None
    if (review.get('v') != AUTOMATED_REVIEW_VERSION
            or review.get('kind') != AUTOMATED_REVIEW_KIND):
        return None
    return review


def read_automated_review(note: str) -> Optional[dict]:
    '''
    The pipeline's review from a note that carries one, or None. For
    callers that only read: nothing is logged or recorded.
    '''
    if not isinstance(note, str) or AUTOMATED_REVIEW_MARKER not in note:
        return None
    return _read_review_block(note)


def _parse_automated_review(claim: FacilityClaim, note: str) -> Optional[dict]:
    '''
    The pipeline's review from its note, or None. A note with no marker
    is an ordinary note. A note with the marker but no block we can
    read is logged, because it means the pipeline and this reader no
    longer agree on the format. The log line carries the claim id only,
    never the note.
    '''
    if not isinstance(note, str) or AUTOMATED_REVIEW_MARKER not in note:
        return None
    review = _read_review_block(note)
    if review is None:
        log.warning(
            'Claim %s: the automated review note has a machine-readable '
            'block that could not be read, so no AI decision was '
            'recorded.',
            claim.id,
        )
    return review


# The decision in the pipeline's review block that means the claim
# passed its review.
REVIEW_DECISION_VALIDATED = 'VALIDATED'


def _review_result_line(decision) -> str:
    return 'Automated review result: {}.'.format(decision)


def _is_reason_for_a_validated_review(reason: Optional[str]) -> bool:
    '''
    Whether a recorded AI decision reason came from a review that
    validated the claim: its first line is the result line
    _describe_automated_review writes for one.
    '''
    if not isinstance(reason, str):
        return False
    return reason.split('\n', 1)[0] == _review_result_line(
        REVIEW_DECISION_VALIDATED
    )


def _describe_automated_review(review: dict) -> str:
    lines = [_review_result_line(review.get('decision'))]
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
    review = _parse_automated_review(claim, note)
    if review is None:
        return
    claim.ai_decision = FacilityClaimAIDecisions.HELD
    claim.ai_decision_reason = _describe_automated_review(review)
    claim.save(update_fields=['ai_decision', 'ai_decision_reason'])


def record_ai_approval(claim: FacilityClaim, user: User) -> None:
    '''
    Mark a claim the pipeline is approving. Sets the fields only; the
    caller saves the claim with the rest of the approval.

    A reason sent with the approval wins. Without one, the reason
    recorded with the pipeline's review is kept only when that review
    validated the claim, which is the usual case: the pipeline posts
    its review and then approves. A reason left by an earlier review
    that held the claim is emptied, so an approval is never explained
    by a reason for not approving.
    '''
    if not is_claims_automation_account(user):
        return
    claim.ai_decision = FacilityClaimAIDecisions.APPROVED
    if claim.status_change_reason:
        claim.ai_decision_reason = claim.status_change_reason
    elif not _is_reason_for_a_validated_review(claim.ai_decision_reason):
        claim.ai_decision_reason = None
