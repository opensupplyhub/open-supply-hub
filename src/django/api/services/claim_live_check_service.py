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
  UNAVAILABLE  no answer in time, the live check is not configured,
               the pipeline said no result is coming (OSDEV-3911), or
               anything went wrong
  CHECKING     none of the above yet

Everything fails open. The claim is saved before a check starts and no
outcome of the check changes it, so the worst a failure can do is tell
the claimant the check is not available.

A claimant only ever receives the status, the fix keys and how many
checks are left: never a score, the model's words or a moderator's
note.
'''
import json
import logging
from datetime import timedelta
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
from api.models.user import User
from api.services.claim_live_check_fixes import (
    FIX_UPLOAD_DOCUMENT,
    FIXES,
    MAX_FIXES,
    fixes_for_review,
)
from api.services.claim_live_review_trigger import trigger_live_review
from api.services.facility_claim_status_service import (
    AUTOMATED_REVIEW_MARKER,
    is_claims_automation_account,
    read_automated_review,
)

logger = logging.getLogger(__name__)

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

# A result for a check the page gave up on is still emailed, but only
# this long after the check started. Later than that the claim is in
# ordinary moderation and its usual emails apply.
LATE_RESULT_WINDOW = timedelta(hours=24)

# OSDEV-3911: the note the pipeline posts when a live check ends
# without a result (it skipped the claim, the review failed, or it
# validated the claim but did not approve it). It has its own marker
# line, so it is never read as a review. The writer is
# build_live_check_status_note in the pipeline's app_moderate_claim.py;
# change the two together.
LIVE_CHECK_STATUS_MARKER = '--- live check status, do not edit ---'
LIVE_CHECK_STATUS_KIND = 'live_check_status'
LIVE_CHECK_STATUS_VERSION = 1
LIVE_CHECK_NO_RESULT = 'no_result'

# The reasons that mean the pipeline never reviewed the claim. A check
# that ended for one of these does not use up one of the claimant's
# checks. Any other reason (a review that failed, a validated claim
# that was not approved) does: the review ran.
NOT_REVIEWED_REASONS = frozenset({
    'review_in_progress',
    'already_reviewed',
    'status_unknown',
    'moderator_notes',
})

# The most checks a claim can ever have, counted or not, so checks that
# do not count cannot be started without end.
MAX_LIVE_CHECK_ATTEMPTS = 2 * MAX_LIVE_CHECKS_PER_CLAIM

# How long the local development stub pretends the pipeline takes.
STUB_DELAY_SECONDS = 5


def is_claim_live_check_active() -> bool:
    return switch_is_active(CLAIM_LIVE_CHECK_SWITCH)


def get_dev_stub() -> str:
    '''
    The local development stub's instruction, or '' when there is none.
    Only honoured with DEBUG on, which is the Local environment alone.
    '''
    return settings.CLAIMS_LIVE_REVIEW_DEV_STUB if settings.DEBUG else ''


def _latest_check(
    claim: FacilityClaim,
    lock: bool = False,
) -> Optional[FacilityClaimLiveCheck]:
    checks = FacilityClaimLiveCheck.objects.filter(claim=claim)
    if lock:
        checks = checks.select_for_update()
    return checks.order_by('-created_at', '-id').first()


def _checks_left(claim: FacilityClaim) -> int:
    if claim.status != FacilityClaimStatuses.PENDING:
        return 0
    reasons = list(
        FacilityClaimLiveCheck.objects
        .filter(claim=claim)
        .values_list('no_result_reason', flat=True)
    )
    if len(reasons) >= MAX_LIVE_CHECK_ATTEMPTS:
        return 0
    used = sum(1 for reason in reasons if reason not in NOT_REVIEWED_REASONS)
    return max(0, MAX_LIVE_CHECKS_PER_CLAIM - used)


def unavailable_state(checks_left: int = 0) -> Dict:
    return {
        'status': FacilityClaimLiveCheckStatuses.UNAVAILABLE,
        'fixes': [],
        'checks_left': checks_left,
    }


def _edited_since(claim: FacilityClaim, check: FacilityClaimLiveCheck) -> bool:
    '''
    Whether the claimant has changed the claim since the check started.
    `claimant_updated_at` is stamped by every claimant edit of a pending
    claim (its fields and its documents) and by nothing a moderator
    does.
    '''
    return (
        claim.claimant_updated_at is not None
        and claim.claimant_updated_at > check.created_at
    )


def _state(
    claim: FacilityClaim,
    check: Optional[FacilityClaimLiveCheck],
) -> Dict:
    '''
    What the claimant is told. No check at all reads as unavailable,
    and so does a check that did not pass once the claimant has changed
    the claim since: its fixes were for the claim as it was, so they
    are not shown again.
    '''
    checks_left = _checks_left(claim)
    stale = (
        check is not None
        and check.status == FacilityClaimLiveCheckStatuses.NOT_PASSED
        and _edited_since(claim, check)
    )
    if check is None or stale:
        return unavailable_state(checks_left)
    state = {
        'status': check.status,
        'fixes': list(check.fixes),
        'checks_left': checks_left,
    }
    # Only present when true, so every other answer keeps its shape:
    # the pipeline said no result is coming, so the page must not
    # promise one by email.
    if check.no_result_reason:
        state['no_result'] = True
    return state


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


def _email_result(
    request,
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
    fixes: List[str],
    no_result: bool = False,
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

    def send():
        try:
            send_claim_live_check_not_passed_email(
                request, claim, fixes, check_again, no_result=no_result
            )
        except Exception:
            logger.exception(
                'Live claim check: the result email for claim %s could '
                'not be sent.',
                claim.id,
            )

    transaction.on_commit(send)


def _email_not_passed(
    request,
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
) -> None:
    '''
    Email the result of a check that a read has just settled as
    NOT_PASSED, unless it has been emailed already. The check row is
    read again under a lock for that decision, so this and the
    pipeline's note (record_live_check_review) can never both send the
    email for one check. Never raises: the claimant is shown the result
    on the page either way.
    '''
    try:
        with transaction.atomic():
            locked = (
                FacilityClaimLiveCheck.objects
                .select_for_update()
                .get(pk=check.pk)
            )
            not_passed = (
                locked.status == FacilityClaimLiveCheckStatuses.NOT_PASSED
            )
            if not_passed and locked.emailed_at is None:
                _email_result(request, claim, locked, list(locked.fixes))
    except Exception:
        logger.exception(
            'Live claim check: the result of check %s of claim %s could '
            'not be emailed.',
            check.id,
            claim.id,
        )


def _stub_fixes(instruction: str) -> List[str]:
    asked = [key.strip() for key in instruction.partition(':')[2].split(',')]
    fixes = [fix for fix in FIXES if fix in asked][:MAX_FIXES]
    return fixes or [FIX_UPLOAD_DOCUMENT]


def _resolve_with_stub(
    request,
    check: FacilityClaimLiveCheck,
    instruction: str,
) -> None:
    '''
    Local development only. Answers the check the way the instruction
    says (`pass`, `not_pass:<fix>,<fix>`, `late_not_pass:<fix>,<fix>`;
    anything else never answers), after a short pretend wait. Only the
    check is filled in: the claim itself is never touched, so a stubbed
    pass leaves the claim PENDING.
    '''
    waited = timezone.now() - check.created_at
    if waited < timedelta(seconds=STUB_DELAY_SECONDS):
        return
    kind = instruction.partition(':')[0].strip().lower()
    if kind == 'pass':
        _finish(check, FacilityClaimLiveCheckStatuses.PASSED)
    elif kind == 'not_pass':
        _finish(
            check,
            FacilityClaimLiveCheckStatuses.NOT_PASSED,
            _stub_fixes(instruction),
        )
        _email_not_passed(request, check.claim, check)
    elif kind == 'late_not_pass':
        # The page is told the check is not available, and the "did not
        # pass" email is sent as for a result that arrived too late.
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
        _email_result(
            request, check.claim, check, _stub_fixes(instruction)
        )
    elif _timed_out(check):
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)


def _for_another_check(review: Dict, check: FacilityClaimLiveCheck) -> bool:
    '''
    Whether the review answers a different check from `check`. The
    pipeline writes the id of the check that asked for a review in its
    note, so a review of an older version of the claim is never taken
    for the answer to a newer check. A review that names no check (the
    scheduled run) is for whichever check is waiting.
    '''
    check_id = review.get('check_id')
    return check_id is not None and check_id != check.id


def _review_since(
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
) -> Optional[Dict]:
    '''
    The pipeline's newest review of the claim posted since `check`
    started and not asked for by another check, or None. Only notes
    written by the claims automation account count, so nobody else can
    answer a check by posting a note that looks like the pipeline's.
    '''
    notes = (
        FacilityClaimReviewNote.objects
        .filter(
            claim=claim,
            created_at__gte=check.created_at,
            note__contains=AUTOMATED_REVIEW_MARKER,
        )
        .select_related('author')
        .order_by('-created_at', '-id')[:5]
    )
    for note in notes:
        if not is_claims_automation_account(note.author):
            continue
        review = read_automated_review(note.note)
        if review is not None and not _for_another_check(review, check):
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


def _resolve(
    request,
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
) -> None:
    '''
    Settle a CHECKING check if the claim now shows an outcome, or if it
    has waited long enough. A settled check is left alone. A check that
    is settled here as NOT_PASSED is emailed to the claimant, as one
    settled by the pipeline's note is.
    '''
    if check.status != FacilityClaimLiveCheckStatuses.CHECKING:
        return

    stub = get_dev_stub()
    if stub:
        _resolve_with_stub(request, check, stub)
        return

    if claim.status == FacilityClaimStatuses.APPROVED:
        _finish(check, FacilityClaimLiveCheckStatuses.PASSED)
        return
    if claim.status != FacilityClaimStatuses.PENDING:
        # Denied or revoked while the claimant waited: a person decided
        # it, and the claimant hears that the usual way.
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
        return

    review = _review_since(claim, check)
    if (review is not None
            and review.get('decision') != REVIEW_DECISION_VALIDATED):
        fixes = _fixes_for(claim, review)
        if fixes:
            _finish(check, FacilityClaimLiveCheckStatuses.NOT_PASSED, fixes)
            _email_not_passed(request, claim, check)
        else:
            # Held for a reason there is no preset line for. Saying
            # nothing specific is better than guessing.
            _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
    elif _timed_out(check):
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)


def _resolved_check(
    request,
    claim: FacilityClaim,
) -> Optional[FacilityClaimLiveCheck]:
    check = _latest_check(claim)
    if check is not None:
        _resolve(request, claim, check)
    return check


def get_live_check_state(request, claim: FacilityClaim) -> Dict:
    '''
    Where the claim's newest live check stands, as
    {status, fixes, checks_left}. Settles the check first if the claim
    now shows an outcome. `request` is only used to build the link in
    the email of a check that is settled here.
    '''
    return _state(claim, _resolved_check(request, claim))


def read_live_check_status(note: str) -> Optional[Dict]:
    '''
    The pipeline's "this live check has no result" block from its note
    (OSDEV-3911), as {check_id, reason}, or None when the note is not
    one or is not in the shape we understand. The block must be the
    last thing in the note, with only whitespace after it: the same
    rule as the review block (_read_review_block). Never raises.
    '''
    if not isinstance(note, str) or LIVE_CHECK_STATUS_MARKER not in note:
        return None
    json_start = note.find('{', note.find(LIVE_CHECK_STATUS_MARKER))
    if json_start == -1:
        return None
    text = note[json_start:]
    try:
        block, end = json.JSONDecoder().raw_decode(text)
    except ValueError:
        return None
    if text[end:].strip() or not isinstance(block, dict):
        return None
    check_id = block.get('check_id')
    reason = block.get('reason')
    if (block.get('v') != LIVE_CHECK_STATUS_VERSION
            or block.get('kind') != LIVE_CHECK_STATUS_KIND
            or block.get('outcome') != LIVE_CHECK_NO_RESULT
            or isinstance(check_id, bool)
            or not isinstance(check_id, int)
            or not isinstance(reason, str)
            or not reason.strip()):
        return None
    return {'check_id': check_id, 'reason': reason.strip()[:200]}


def _record_no_result(
    request,
    claim: FacilityClaim,
    status_block: Dict,
) -> None:
    '''
    The pipeline said the check it names ended without a result. The
    check stops waiting at once and remembers why.

    A check the page is still waiting on is simply settled: the page
    reads the answer on its next poll and tells the claimant a person
    will review the claim. A check the page had already given up on was
    answered "we will email you the result", so that claimant is
    emailed that a person will review the claim.

    Left alone: a check that is not the claim's newest (the claimant
    has moved on), one that already has a result, a reason or an email,
    one whose review was never requested, and one older than
    LATE_RESULT_WINDOW. The row is locked for the decision.
    '''
    with transaction.atomic():
        check = _latest_check(claim, lock=True)
        if check is None or check.id != status_block['check_id']:
            return
        if check.no_result_reason or check.emailed_at is not None:
            return
        waiting = check.status == FacilityClaimLiveCheckStatuses.CHECKING
        gave_up = (
            check.status == FacilityClaimLiveCheckStatuses.UNAVAILABLE
            and check.review_requested
        )
        if not waiting and not gave_up:
            return
        if timezone.now() - check.created_at > LATE_RESULT_WINDOW:
            return

        check.status = FacilityClaimLiveCheckStatuses.UNAVAILABLE
        check.fixes = []
        check.no_result_reason = status_block['reason']
        check.save(update_fields=[
            'status', 'fixes', 'no_result_reason', 'updated_at',
        ])
        logger.info(
            'Live claim check ended without a result: claim=%s check=%s '
            'reason=%s',
            claim.id,
            check.id,
            check.no_result_reason,
        )
        if gave_up:
            _email_result(request, claim, check, [], no_result=True)


def record_live_check_review(
    request,
    claim: FacilityClaim,
    user: User,
    note: str,
) -> None:
    '''
    Called when an internal note is posted on a claim. If it is the
    pipeline's review and the pipeline held the claim, the claim's
    newest check is settled here, at once, and the claimant is emailed
    the preset fixes and a link back to the claim, whether or not their
    page is still waiting. When the review names nothing there is a
    preset line for, the email says a person will review the claim.

    Two kinds of check take a result: one still CHECKING, and one that
    ended UNAVAILABLE after its review was requested, which is a check
    the page gave up on (the pipeline often needs longer than the page
    waits). Left alone: a check that has an answer or was already
    emailed, so one check never sends two emails; a check whose review
    could not be requested; and a check that started more than
    LATE_RESULT_WINDOW ago. Without the last two, a claimant could get
    a "did not pass" email days later from the pipeline's scheduled
    run. A review that an older check asked for is left alone too: it
    is about the claim as it was before the claimant's edit. The check
    row is locked for the decision, so two notes arriving at once
    cannot both settle it.

    A pass sends nothing from here, because the approval that follows
    sends the usual approval email.

    The pipeline's other note, "this live check has no result"
    (OSDEV-3911), is handled here too: see _record_no_result.

    Never raises and never undoes the note: a failure in here is logged
    and the check is left for the next poll or the timeout.
    '''
    try:
        if not is_claim_live_check_active() or get_dev_stub():
            return
        if claim.status != FacilityClaimStatuses.PENDING:
            return
        if not is_claims_automation_account(user):
            return
        status_block = read_live_check_status(note)
        if status_block is not None:
            _record_no_result(request, claim, status_block)
            return
        review = read_automated_review(note)
        if (review is None
                or review.get('decision') == REVIEW_DECISION_VALIDATED):
            return
        with transaction.atomic():
            check = _latest_check(claim, lock=True)
            if check is None or check.emailed_at is not None:
                return
            if _for_another_check(review, check):
                return
            waiting = check.status == FacilityClaimLiveCheckStatuses.CHECKING
            gave_up = (
                check.status == FacilityClaimLiveCheckStatuses.UNAVAILABLE
                and check.review_requested
            )
            if not waiting and not gave_up:
                return
            if timezone.now() - check.created_at > LATE_RESULT_WINDOW:
                return

            fixes = _fixes_for(claim, review)
            _finish(
                check,
                FacilityClaimLiveCheckStatuses.NOT_PASSED if fixes
                else FacilityClaimLiveCheckStatuses.UNAVAILABLE,
                fixes,
            )
            _email_result(request, claim, check, fixes)
    except Exception:
        logger.exception(
            'Live claim check: the review of claim %s could not be '
            'recorded or emailed.',
            claim.id,
        )


def start_live_check(
    request,
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

    No new check is started while one is running, when the last one
    gave an answer and the claimant has not changed the claim since
    (the pipeline would only say the same), or when the claim is
    decided or has used all its checks. When the live check is not
    configured nothing is recorded and the state is UNAVAILABLE.
    '''
    check = _resolved_check(request, claim)

    running_or_answered = (
        check is not None
        and check.status != FacilityClaimLiveCheckStatuses.UNAVAILABLE
        and (check.status == FacilityClaimLiveCheckStatuses.CHECKING
             or not _edited_since(claim, check))
    )
    if running_or_answered or _checks_left(claim) == 0:
        return _state(claim, check), None

    stub = get_dev_stub()
    if not stub and not settings.CLAIMS_LIVE_REVIEW_FUNCTION:
        return _state(claim, None), None

    check = FacilityClaimLiveCheck.objects.create(claim=claim)
    logger.info(
        'Live claim check started: claim=%s check=%s', claim.id, check.id
    )
    return _state(claim, check), (None if stub else check)


def request_review(
    claim: FacilityClaim,
    check: FacilityClaimLiveCheck,
) -> Dict:
    '''
    Ask the pipeline to review the claim for a check that has just been
    committed, and return the check's state. If the request fails the
    check ends UNAVAILABLE and is marked as never requested, so nothing
    about it is ever emailed.
    '''
    if not trigger_live_review(claim.id, check.id):
        check.status = FacilityClaimLiveCheckStatuses.UNAVAILABLE
        check.review_requested = False
        check.save(
            update_fields=['status', 'review_requested', 'updated_at']
        )
    return _state(claim, check)


def give_up_live_check(request, claim: FacilityClaim) -> Dict:
    '''
    The claimant's page has waited its minute and has stopped asking.
    The check ends UNAVAILABLE, which is what the page was shown; a
    result that arrives later still settles it and is emailed (see
    record_live_check_review). A result that is already there is
    returned instead.
    '''
    check = _resolved_check(request, claim)
    if (check is not None
            and check.status == FacilityClaimLiveCheckStatuses.CHECKING):
        _finish(check, FacilityClaimLiveCheckStatuses.UNAVAILABLE)
    return _state(claim, check)
