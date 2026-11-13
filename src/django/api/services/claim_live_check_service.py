'''
The live check of a claim (OSDEV-3804): right after a claimant submits
a claim, the claims automation pipeline is asked to review that one
claim now, and the claim form waits for the answer.

It is the review the pipeline already runs on a schedule, so nothing is
decided here. The pipeline approves the claim or posts its review note
through the API it always uses, and this service reads the outcome off
the claim:

  PASSED       the claim is APPROVED
  NOT_PASSED   the pipeline posted its review note and left the claim
               for a moderator; the note's machine-readable block is
               turned into preset fixes (claim_live_check_fixes)
  UNAVAILABLE  no answer in time, the live check is not configured, or
               anything went wrong
  CHECKING     none of the above yet

Everything fails open. The claim is saved before a check starts and no
outcome of the check changes it, so the worst a failure can do is tell
the claimant the check is not available. The claim then waits for a
moderator as it always has.

A claimant only ever receives the status, the fix keys and how many
checks are left: never a score, the model's words or a moderator's
note.
'''
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from waffle import switch_is_active

from api.constants import (
    FacilityClaimLiveCheckStatuses,
    FacilityClaimStatuses,
)
from api.mail import send_claim_live_check_not_passed_email
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_claim_attachments import (
    FacilityClaimAttachments,
)
from api.models.facility.facility_claim_live_check import (
    FacilityClaimLiveCheck,
)
from api.models.facility.facility_claim_review_note import (
    FacilityClaimReviewNote,
)
from api.services.claim_live_check_fixes import (
    FIX_UPLOAD_DOCUMENT,
    FIXES,
    MAX_FIXES,
    fixes_for_review,
)
from api.services.claim_live_review_trigger import (
    is_live_review_configured,
    trigger_live_review,
)
from api.models.user import User
from api.services.facility_claim_status_service import (
    AUTOMATED_REVIEW_MARKER,
    is_claims_automation_account,
    read_automated_review,
)

logger = logging.getLogger(__name__)

# The whole feature ships behind this switch (created off by migration
# 0272). Off, the endpoint answers 404 and the claim form is unchanged.
CLAIM_LIVE_CHECK_SWITCH = 'claim_live_check'

# A claimant can fix their pending claim and check again, this many
# times in all per claim.
MAX_LIVE_CHECKS_PER_CLAIM = 3

# How long a check may stay CHECKING. The claim form waits the same
# time before it stops asking.
LIVE_CHECK_TIMEOUT_SECONDS = 60

# The decision in the pipeline's review block that means it is about to
# approve the claim. It posts the note first and approves after, so a
# note with this decision is not an outcome yet.
REVIEW_DECISION_VALIDATED = 'VALIDATED'

# A page that is waiting on a check asks for it every few seconds. One
# that has not asked for this long has been left, and a result that
# arrives then is emailed to the claimant instead.
PAGE_LEFT_AFTER_SECONDS = 10

# A result for a check the page gave up on is still emailed, but only
# this long after the check started. Later than that the claim is in
# ordinary moderation and its usual emails apply.
LATE_RESULT_WINDOW = timedelta(hours=24)

# The local development stub (settings.CLAIMS_LIVE_REVIEW_DEV_STUB).
STUB_PASS = 'pass'
STUB_TIMEOUT = 'timeout'
STUB_NOT_PASS = 'not_pass'
# The page is told the check is not available, and the "did not pass"
# email is sent as it would be for a result that arrived too late.
STUB_LATE_NOT_PASS = 'late_not_pass'
# How long the stub pretends the pipeline takes.
STUB_DELAY_SECONDS = 5

_ANSWERED = (
    FacilityClaimLiveCheckStatuses.PASSED,
    FacilityClaimLiveCheckStatuses.NOT_PASSED,
)


def is_claim_live_check_active() -> bool:
    return switch_is_active(CLAIM_LIVE_CHECK_SWITCH)


def get_dev_stub() -> str:
    '''
    The local development stub's instruction, or '' when there is none.
    Only ever honoured with DEBUG on, which is the Local environment
    alone: settings.py already drops the value elsewhere, and this
    second check means a settings override cannot bring it back.
    '''
    if not settings.DEBUG:
        return ''
    return (settings.CLAIMS_LIVE_REVIEW_DEV_STUB or '').strip()


def _is_available() -> bool:
    return bool(get_dev_stub()) or is_live_review_configured()


def _latest_check(claim: FacilityClaim) -> Optional[FacilityClaimLiveCheck]:
    return (
        FacilityClaimLiveCheck.objects
        .filter(claim=claim)
        .order_by('-created_at', '-id')
        .first()
    )


def _checks_left(claim: FacilityClaim) -> int:
    if claim.status != FacilityClaimStatuses.PENDING:
        return 0
    used = FacilityClaimLiveCheck.objects.filter(claim=claim).count()
    return max(0, MAX_LIVE_CHECKS_PER_CLAIM - used)


def unavailable_state(checks_left: int = 0) -> Dict:
    return {
        'status': FacilityClaimLiveCheckStatuses.UNAVAILABLE,
        'fixes': [],
        'checks_left': checks_left,
    }


def _state(
    claim: FacilityClaim,
    check: Optional[FacilityClaimLiveCheck],
) -> Dict:
    '''What the claimant is told. No check at all reads as unavailable.'''
    checks_left = _checks_left(claim)
    if check is None:
        return unavailable_state(checks_left)
    return {
        'status': check.status,
        'fixes': list(check.fixes),
        'checks_left': checks_left,
    }


def _finish(
    check: FacilityClaimLiveCheck,
    status: str,
    fixes: Optional[List[str]] = None,
) -> None:
    check.status = status
    check.fixes = fixes or []
    check.save(update_fields=['status', 'fixes', 'updated_at'])


def _timed_out(check: FacilityClaimLiveCheck) -> bool:
    deadline = check.created_at + timedelta(
        seconds=LIVE_CHECK_TIMEOUT_SECONDS
    )
    return timezone.now() >= deadline


def _stub_fixes(instruction: str) -> List[str]:
    _, _, listed = instruction.partition(':')
    asked = [key.strip() for key in listed.split(',')]
    fixes = [fix for fix in FIXES if fix in asked][:MAX_FIXES]
    return fixes or [FIX_UPLOAD_DOCUMENT]


def _resolve_with_stub(
    check: FacilityClaimLiveCheck,
    instruction: str,
) -> None:
    '''
    Local development only. Answers the check the way the instruction
    says, after a short pretend wait. It only fills in the check: the
    claim itself is never touched, so a stubbed pass leaves the claim
    PENDING.
    '''
    waited = timezone.now() - check.created_at
    if waited < timedelta(seconds=STUB_DELAY_SECONDS):
        return
    kind = instruction.partition(':')[0].strip().lower()
    if kind == STUB_PASS:
        _finish(check, FacilityClaimLiveCheckStatuses.PASSED)
    elif kind == STUB_NOT_PASS:
        _finish(
            check,
            FacilityClaimLiveCheckStatuses.NOT_PASSED,
            _stub_fixes(instruction),
        )
    elif kind == STUB_LATE_NOT_PASS:
        # The page gives up, then the result "arrives" and is emailed.
        # The check stays UNAVAILABLE, which is what the page is shown;
        # the email goes to the console in local development.
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
        _email_result(None, check.claim, check, _stub_fixes(instruction))
    elif _timed_out(check):
        # `timeout`, and anything unrecognised, never answers.
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)


def _review_since(claim: FacilityClaim, since: datetime) -> Optional[Dict]:
    '''
    The pipeline's newest review of the claim posted at or after
    `since`, or None. Only notes written by the claims automation
    account count, so nobody else can answer a check by posting a note
    that looks like the pipeline's.
    '''
    notes = (
        FacilityClaimReviewNote.objects
        .filter(
            claim=claim,
            created_at__gte=since,
            note__contains=AUTOMATED_REVIEW_MARKER,
        )
        .select_related('author')
        .order_by('-created_at', '-id')[:5]
    )
    for note in notes:
        if not is_claims_automation_account(note.author):
            continue
        review = read_automated_review(note.note)
        if review is not None:
            return review
    return None


def _fixes_for(claim: FacilityClaim, review: Dict) -> List[str]:
    return fixes_for_review(
        review,
        claimant_email=claim.contributor.admin.email,
        has_attachments=FacilityClaimAttachments.objects.filter(
            claim=claim
        ).exists(),
    )


def _resolve(claim: FacilityClaim, check: FacilityClaimLiveCheck) -> None:
    '''
    Settle a CHECKING check if the claim now shows an outcome, or if it
    has waited long enough. A settled check is left alone.
    '''
    if check.status != FacilityClaimLiveCheckStatuses.CHECKING:
        return

    stub = get_dev_stub()
    if stub:
        _resolve_with_stub(check, stub)
        return

    if claim.status == FacilityClaimStatuses.APPROVED:
        _finish(check, FacilityClaimLiveCheckStatuses.PASSED)
        return
    if claim.status != FacilityClaimStatuses.PENDING:
        # Denied or revoked while the claimant waited: a person decided
        # it, and the claimant hears that the usual way.
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
        return

    review = _review_since(claim, check.created_at)
    held = (
        review is not None
        and review.get('decision') != REVIEW_DECISION_VALIDATED
    )
    if held:
        fixes = _fixes_for(claim, review)
        if fixes:
            _finish(check, FacilityClaimLiveCheckStatuses.NOT_PASSED, fixes)
        else:
            # Held for a reason there is no preset line for. Saying
            # nothing specific is better than guessing.
            _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
        return

    if _timed_out(check):
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)


def _review_was_requested(check: FacilityClaimLiveCheck) -> bool:
    '''
    False for a check whose trigger failed: `last_polled_at` is set when
    a check starts and cleared when its review could not be requested.
    '''
    return check.last_polled_at is not None


def _edited_since(claim: FacilityClaim, check: FacilityClaimLiveCheck) -> bool:
    return (
        claim.claimant_updated_at is not None
        and claim.claimant_updated_at > check.created_at
    )


def get_live_check_state(claim: FacilityClaim) -> Dict:
    '''
    Where the claim's newest live check stands, as
    {status, fixes, checks_left}. Settles the check first if the claim
    now shows an outcome.
    '''
    check = _latest_check(claim)
    if check is not None:
        _resolve(claim, check)
        if check.status == FacilityClaimLiveCheckStatuses.CHECKING:
            # The claimant's page is still waiting on this check.
            check.last_polled_at = timezone.now()
            check.save(update_fields=['last_polled_at'])
    return _state(claim, check)


def _page_is_waiting(check: FacilityClaimLiveCheck) -> bool:
    '''
    Whether the claimant's page is still asking for this check. The
    page stops asking after its minute, so a check older than that has
    been left whatever its last poll says.
    '''
    if check.last_polled_at is None or _timed_out(check):
        return False
    waited = timezone.now() - check.last_polled_at
    return waited < timedelta(seconds=PAGE_LEFT_AFTER_SECONDS)


def _send_result_email(request, claim, fixes, check_again) -> None:
    try:
        send_claim_live_check_not_passed_email(
            request, claim, fixes, check_again
        )
    except Exception:
        logger.exception(
            'Live claim check: the result email for claim %s could not '
            'be sent.',
            claim.id,
        )


def _email_result(
    request,
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
    fixes: List[str],
) -> None:
    '''
    Record that the check's result is being emailed and send the email
    once the surrounding transaction has committed, so a note that is
    rolled back never emails. `emailed_at` is written first, under the
    caller's lock on the check, which is what stops a second note from
    sending a second email. If the send then fails it is logged and not
    retried: one missing email is the cheaper failure than two.
    '''
    check.emailed_at = timezone.now()
    check.save(update_fields=['emailed_at', 'updated_at'])
    check_again = bool(fixes) and _checks_left(claim) > 0
    transaction.on_commit(
        lambda: _send_result_email(request, claim, fixes, check_again)
    )


def _settle_from_review(request, claim: FacilityClaim, review: Dict) -> None:
    '''
    Settle the claim's newest check from the pipeline's review, and
    email the claimant unless their page is still waiting to show it.

    Two kinds of check take a result: one still CHECKING, and one that
    ended UNAVAILABLE after it was started, which is a check the page
    gave up on (the pipeline often needs longer than the page waits).
    The second is the common case for the email: the claimant was told
    the check was not available and that an email would follow.

    Left alone: a check that has an answer or was already emailed (so
    one check never sends two emails); a check whose review was never
    requested, because the trigger failed; and a check that started
    more than LATE_RESULT_WINDOW ago. Without the last two, a claimant
    could get a "did not pass" email days later from the pipeline's
    scheduled run.

    The check row is locked for the decision, so two notes arriving at
    once cannot both settle it. When the review names nothing there is
    a preset line for, the email says a person will review the claim.
    '''
    check = (
        FacilityClaimLiveCheck.objects
        .select_for_update()
        .filter(claim=claim)
        .order_by('-created_at', '-id')
        .first()
    )
    if check is None or check.emailed_at is not None:
        return
    waiting = check.status == FacilityClaimLiveCheckStatuses.CHECKING
    gave_up = (
        check.status == FacilityClaimLiveCheckStatuses.UNAVAILABLE
        and _review_was_requested(check)
    )
    if not waiting and not gave_up:
        return
    if timezone.now() - check.created_at > LATE_RESULT_WINDOW:
        return

    fixes = _fixes_for(claim, review)
    page_is_waiting = waiting and _page_is_waiting(check)
    if fixes:
        _finish(check, FacilityClaimLiveCheckStatuses.NOT_PASSED, fixes)
    else:
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
    if not page_is_waiting:
        _email_result(request, claim, check, fixes)


def record_live_check_review(
    request,
    claim: FacilityClaim,
    user: User,
    note: str,
) -> None:
    '''
    Called when an internal note is posted on a claim. If it is the
    pipeline's review of a claim whose live check is still waiting or
    has already timed out, and the pipeline held the claim, the check
    is settled here, at once, rather than on the claimant's next poll.
    That is what lets the result reach a claimant whose page is no
    longer showing it: when their page has stopped asking, or gave up
    after its minute, they are emailed the preset fixes and a link back
    to the claim. A claimant whose page is still asking sees the result
    there and gets no email.

    One email at most per check (see _settle_from_review). A pass sends
    nothing from here, because the approval that follows sends the
    usual approval email, however late it comes.

    Never raises and never undoes the note: a failure in here is logged
    and the check is left for the next poll or the timeout. The email
    goes out only after the note has committed.
    '''
    try:
        if not is_claim_live_check_active() or get_dev_stub():
            return
        if claim.status != FacilityClaimStatuses.PENDING:
            return
        if not is_claims_automation_account(user):
            return
        review = read_automated_review(note)
        if (review is None
                or review.get('decision') == REVIEW_DECISION_VALIDATED):
            return
        with transaction.atomic():
            _settle_from_review(request, claim, review)
    except Exception:
        logger.exception(
            'Live claim check: the review of claim %s could not be '
            'recorded or emailed.',
            claim.id,
        )


def start_live_check(
    claim: FacilityClaim,
) -> Tuple[Dict, Optional[FacilityClaimLiveCheck]]:
    '''
    Start a live check of the claim. Returns its state, as
    get_live_check_state does, and the new check when its review still
    has to be requested.

    The caller holds a row lock on the claim, so two requests cannot
    both count the checks used and both start one. Nothing is sent to
    the pipeline in here: the caller commits, releasing the lock, and
    then calls request_review with the returned check. That keeps a
    network call out of the lock, and means a rollback can never leave
    a review running for a check that was not recorded.

    No new check is started, and the newest one is returned as it
    stands, when:
      - the claim is no longer PENDING;
      - a check is still running (a double click);
      - the last check gave an answer and the claimant has not changed
        the claim since, so the pipeline would only say the same;
      - the claim has used all its checks.
    When the live check is not configured nothing is recorded and the
    state is UNAVAILABLE.
    '''

    check = _latest_check(claim)
    if check is not None:
        _resolve(claim, check)

    if claim.status != FacilityClaimStatuses.PENDING:
        return _state(claim, check), None
    if check is not None:
        if check.status == FacilityClaimLiveCheckStatuses.CHECKING:
            return _state(claim, check), None
        if check.status in _ANSWERED and not _edited_since(claim, check):
            return _state(claim, check), None
    if _checks_left(claim) == 0:
        return _state(claim, check), None
    if not _is_available():
        return _state(claim, None), None

    check = FacilityClaimLiveCheck.objects.create(
        claim=claim,
        last_polled_at=timezone.now(),
    )
    logger.info(
        'Live claim check started: claim=%s check=%s', claim.id, check.id
    )
    return _state(claim, check), (None if get_dev_stub() else check)


def request_review(
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
) -> Dict:
    '''
    Ask the pipeline to review the claim for a check that has just been
    committed, and return the check's state. If the request fails the
    check ends UNAVAILABLE and is marked as never requested, so nothing
    about it is ever emailed. Never raises.
    '''
    try:
        requested = trigger_live_review(claim.id)
    except Exception:
        logger.exception(
            'Live claim check: the review of claim %s could not be '
            'requested.',
            claim.id,
        )
        requested = False
    if not requested:
        check.status = FacilityClaimLiveCheckStatuses.UNAVAILABLE
        check.last_polled_at = None
        check.save(update_fields=['status', 'last_polled_at', 'updated_at'])
    return _state(claim, check)


def give_up_live_check(claim: FacilityClaim) -> Dict:
    '''
    The claimant's page has waited its minute and is showing "not
    available". Record that, so a result that arrives from now on is
    emailed rather than assumed to be seen. A result that is already
    there is returned instead.
    '''
    check = _latest_check(claim)
    if check is not None:
        _resolve(claim, check)
        if check.status == FacilityClaimLiveCheckStatuses.CHECKING:
            _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
    return _state(claim, check)
    return _state(claim, check)
