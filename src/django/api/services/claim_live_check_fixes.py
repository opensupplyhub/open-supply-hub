'''
The one place that turns the claims automation pipeline's review of a
claim into what the claimant is told to fix (OSDEV-3804).

The pipeline scores a claim on a handful of checks and posts the scores
in the machine-readable block of its review note. A claimant never sees
scores or the model's own words: they see between one and five preset
lines, and this module decides which. It returns keys only. The text of
each line lives with the claim form, which is the only place that shows
it.

Nothing here reads the database or the settings, so every rule can be
tested with plain values.
'''
from typing import Dict, List, Set

# The pipeline's checks, by the names it scores them under.
CHECK_ADDRESS = 'address_match_score'
CHECK_NAME = 'name_verification_score'
CHECK_DOCUMENTS = 'documentation_quality_score'
CHECK_AFFILIATION = 'affiliation_verification_score'
CHECK_MANAGER = 'manager_supervisor_score'

CHECKS = (
    CHECK_ADDRESS,
    CHECK_NAME,
    CHECK_DOCUMENTS,
    CHECK_AFFILIATION,
    CHECK_MANAGER,
)

# The preset fixes, in the order they are shown. The first one is the
# field the claimant is taken to when they choose to go back.
FIX_WORK_EMAIL = 'work_email'
FIX_UPLOAD_DOCUMENT = 'upload_document'
FIX_UNREADABLE_DOCUMENT = 'unreadable_document'
FIX_NAME_AND_COMPANY_DOCUMENT = 'name_and_company_document'
FIX_COMPANY_NAME_DOCUMENT = 'company_name_document'
FIX_COMPANY_ADDRESS_DOCUMENT = 'company_address_document'

FIXES = (
    FIX_WORK_EMAIL,
    FIX_UPLOAD_DOCUMENT,
    FIX_UNREADABLE_DOCUMENT,
    FIX_NAME_AND_COMPANY_DOCUMENT,
    FIX_COMPANY_NAME_DOCUMENT,
    FIX_COMPANY_ADDRESS_DOCUMENT,
)

MAX_FIXES = 5

# Mailbox providers anyone can sign up with. An address at one of these
# says nothing about where its owner works.
FREE_MAIL_DOMAINS = frozenset({
    '126.com',
    '163.com',
    'aol.com',
    'foxmail.com',
    'gmail.com',
    'gmx.com',
    'gmx.de',
    'googlemail.com',
    'hotmail.co.uk',
    'hotmail.com',
    'hotmail.fr',
    'icloud.com',
    'live.com',
    'mail.com',
    'mail.ru',
    'me.com',
    'msn.com',
    'naver.com',
    'outlook.com',
    'proton.me',
    'protonmail.com',
    'qq.com',
    'rediffmail.com',
    'sina.com',
    'yahoo.co.in',
    'yahoo.co.jp',
    'yahoo.co.uk',
    'yahoo.com',
    'yandex.com',
    'yandex.ru',
    'zoho.com',
})


def is_free_mail(email: str) -> bool:
    '''True when the address is at a mailbox provider open to anyone.'''
    _, _, domain = (email or '').strip().lower().rpartition('@')
    return domain in FREE_MAIL_DOMAINS


def _as_dict(value) -> Dict:
    return value if isinstance(value, dict) else {}


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def failed_checks(review: Dict) -> Set[str]:
    '''
    The checks the pipeline failed the claim on, read from its review
    block.

    A check failed when its score is under the threshold the pipeline
    ran with, or when the pipeline gave a reason for it: it only writes
    reasons for the checks that fell short. Both come from the block
    itself, so no threshold is kept here. A check the pipeline skipped
    for this claim did not fail. Anything in the block that is not the
    shape we expect is ignored rather than raised on.
    '''
    scores = _as_dict(review.get('confidence_scores'))
    thresholds = _as_dict(
        _as_dict(review.get('threshold_config_snapshot')).get(
            'score_thresholds'
        )
    )
    reasoning = _as_dict(review.get('reasoning'))
    skipped = review.get('skipped_dimensions')
    skipped = skipped if isinstance(skipped, (dict, list)) else ()

    failed = set()
    for check in CHECKS:
        if check in skipped:
            continue
        score = scores.get(check)
        threshold = thresholds.get(check)
        below = (
            _is_number(score)
            and _is_number(threshold)
            and score < threshold
        )
        if below or check in reasoning:
            failed.add(check)
    return failed


def fixes_for_review(
    review: Dict,
    claimant_email: str,
    has_attachments: bool,
) -> List[str]:
    '''
    The preset fixes for a claim the pipeline held, as keys from FIXES
    in display order, at most MAX_FIXES. Empty when the review names no
    check we know how to explain.

      who the claimant is (affiliation) failed, free-mail address
          -> use a work email
      who the claimant is (affiliation) failed, any other address
          -> add a document showing their name and company
      manager or supervisor failed
          -> add a document showing their name and company
      company name failed
          -> add an official document showing the company name
      company address failed
          -> add an official document showing the company address
      the claim has no documents
          -> upload a document
      documents failed and the claim has documents
          -> a document could not be read
    '''
    failed = failed_checks(review)
    if not failed:
        return []

    chosen = set()
    if CHECK_AFFILIATION in failed:
        chosen.add(
            FIX_WORK_EMAIL if is_free_mail(claimant_email)
            else FIX_NAME_AND_COMPANY_DOCUMENT
        )
    if CHECK_MANAGER in failed:
        chosen.add(FIX_NAME_AND_COMPANY_DOCUMENT)
    if CHECK_NAME in failed:
        chosen.add(FIX_COMPANY_NAME_DOCUMENT)
    if CHECK_ADDRESS in failed:
        chosen.add(FIX_COMPANY_ADDRESS_DOCUMENT)
    if not has_attachments:
        chosen.add(FIX_UPLOAD_DOCUMENT)
    elif CHECK_DOCUMENTS in failed:
        chosen.add(FIX_UNREADABLE_DOCUMENT)

    return [fix for fix in FIXES if fix in chosen][:MAX_FIXES]
