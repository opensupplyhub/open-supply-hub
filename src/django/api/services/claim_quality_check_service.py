'''
Advisory, LLM-backed data-quality warnings for the name and address a
claimant asserts for a production location (OSDEV-3489), on the claim
form and on the approved-claim details form.

Mirrors the SLC submission quality check (SubmissionQualityProcessor),
with two deliberate differences:

- The check is its own endpoint (POST /api/facilities/{id}/claim/
  quality-check/) called before the write, not a 409 on the write. On
  the claim form the values are entered on the Business step and the
  claim is submitted, with document uploads, two steps later; bouncing
  that submission would send the claimant back and make them re-upload.
- Dismissed warnings are recorded. SLC stores nothing because no one
  reviews an approved SLC by hand; a claim is decided by a moderator,
  so the write endpoints accept the warnings the claimant continued
  past and leave an INTERNAL review note listing them.

Everything here is advisory and fails open: the claimant is never
blocked, and any failure of the model call means no warnings.
'''
import json
import logging
from typing import Dict, List, Optional, Tuple

from waffle import switch_is_active

from api.constants import FacilityClaimReviewNoteTypes
from api.models.facility.facility import Facility
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_claim_review_note import (
    FacilityClaimReviewNote,
)
from api.models.user import User
from api.services.claim_contribution_service import (
    CLAIM_NAME_ADDRESS_EDIT_SWITCH,
    same_claimed_value,
)
from api.services.claim_quality_service import ClaimQualityService
from api.services.claim_quality_warnings import WARNING_TITLES
from api.services.facility_claim_review_note_service import (
    create_review_note,
)
from countries.lib.countries import COUNTRY_NAMES

logger = logging.getLogger(__name__)

# Kill switch for the LLM call alone, toggleable in the Django admin
# without a deploy (created active by migration 0244). The check also
# requires enable_claim_name_address_edit, the switch the whole
# editable name/address feature ships behind, so it stays dark with the
# fields and can still be turned off on its own if the model misbehaves.
# If the Switch row is ever missing, waffle falls back to
# WAFFLE_SWITCH_DEFAULT (False), so the check disables rather than
# blocking claims.
CLAIM_QUALITY_CHECK_SWITCH = 'claim_quality_check'

# Verdicts that judge one field on its own. They are not reported when
# that field is the one already listed: the claimant neither wrote nor
# changed it, so there is nothing to warn them about. The remaining
# verdicts (multiple_locations, different_location) judge the pair and
# are always reported.
_NAME_ONLY_VERDICTS = frozenset({'name_quality'})
_ADDRESS_ONLY_VERDICTS = frozenset({
    'address_quality',
    'address_country_mismatch',
})

# Which form the values came through, recorded in the note and the log.
SOURCE_CLAIM_FORM = 'claim_form'
SOURCE_CLAIMED_DETAILS = 'claimed_details'

_SOURCE_DESCRIPTIONS = {
    SOURCE_CLAIM_FORM: 'submitting the claim form',
    SOURCE_CLAIMED_DETAILS: 'updating the claimed facility details',
}


def is_claim_quality_check_active() -> bool:
    return (
        switch_is_active(CLAIM_NAME_ADDRESS_EDIT_SWITCH)
        and switch_is_active(CLAIM_QUALITY_CHECK_SWITCH)
    )


def listed_name_and_address(facility: Facility) -> Tuple[str, str]:
    '''
    The name and address the location page currently shows, which is
    what a claimant is confirming or correcting. Approving a claim
    records its name and address as a contribution but never rewrites
    facility.name or facility.address, so for a claimed location they
    are the approved claim's values where it asserts them, and the
    facility's own otherwise. (A location with an approved claim cannot
    be claimed again, so on the claim form this is always the facility's
    own listing.)
    '''
    name = facility.name or ''
    address = facility.address or ''
    claim = facility.get_approved_claim()
    if claim is not None:
        name = (claim.facility_name_english or '').strip() or name
        address = (claim.facility_address or '').strip() or address
    return name, address


def check_claim_quality(
    facility: Facility,
    name: str,
    address: str,
    contributor_id: int,
    quality_service: Optional[ClaimQualityService] = None,
) -> List[Dict]:
    '''
    Evaluate the claimed name and address for `facility` and return the
    warnings to show the claimant, as [{type, title, message}] - the
    same shape as the SLC `warnings` array. Empty when nothing is
    flagged, when either switch is off, when the values are the ones
    the location already lists (nothing new is being asserted, so
    there is nothing to judge and no call to pay for), or when the
    model call fails (the service logs that; this fails open).

    A blank value asserts nothing and stands for the listed one, the
    way the write path backfills it. "The same" is judged the way the
    write path judges whether an address changed (same_claimed_value),
    so the check never warns about an edit the write treats as a no-op.
    When only one of the two values is new, the verdicts that judge the
    other on its own are not reported.

    Every evaluated pair logs one INFO line carrying the judged fields,
    so that what the check saw can be compared with what was later
    submitted (see record_claim_quality_outcome). Only the name, address
    and country are logged: they are what the model judges and the
    published record of a location anyway. Nothing else in the request
    reaches the log.
    '''
    if not is_claim_quality_check_active():
        return []

    listed_name, listed_address = listed_name_and_address(facility)
    name = (name or '').strip() or listed_name
    address = (address or '').strip() or listed_address
    name_changed = not same_claimed_value(name, listed_name)
    address_changed = not same_claimed_value(address, listed_address)
    if not name_changed and not address_changed:
        logger.info(
            'Claim quality check skipped (values unchanged): '
            'contributor=%s facility=%s',
            contributor_id,
            facility.id,
        )
        return []

    country_code = facility.country_code
    country_name = COUNTRY_NAMES.get(country_code, country_code or '')
    verdicts = (quality_service or ClaimQualityService()).evaluate(
        name=name,
        address=address,
        country_name=country_name,
        current_name=listed_name,
        current_address=listed_address,
    )

    warnings = []
    if verdicts is not None:
        suppressed = set()
        if not name_changed:
            suppressed |= _NAME_ONLY_VERDICTS
        if not address_changed:
            suppressed |= _ADDRESS_ONLY_VERDICTS
        for warning_type, title in WARNING_TITLES.items():
            if warning_type in suppressed:
                continue
            # A warning the verdict schema does not know is skipped
            # rather than raised on, so a vocabulary mismatch degrades
            # to a missing warning on an endpoint that must fail open.
            verdict = getattr(verdicts, warning_type, None)
            if verdict is not None and verdict.flagged:
                warnings.append({
                    'type': warning_type,
                    'title': title,
                    'message': verdict.reason,
                })

    # Logged whether or not anything was flagged, and when the model
    # call failed too (model=failed, with an empty list), so that every
    # evaluated pair has a line to compare against the outcome line of
    # the write that follows, if any, and a fail-open empty list can be
    # told from a clean verdict.
    logger.info(
        'Claim quality check evaluated: contributor=%s facility=%s '
        'model=%s warnings=%s fields=%s',
        contributor_id,
        facility.id,
        'ok' if verdicts is not None else 'failed',
        [warning['type'] for warning in warnings],
        _describe_fields(name, address, country_code),
    )
    return warnings


def record_claim_quality_outcome(
    claim: FacilityClaim,
    acting_user: User,
    dismissed_warnings: List[Dict],
    source: str,
) -> Optional[FacilityClaimReviewNote]:
    '''
    Called by a write that stored a claimed name or address, after the
    claim is saved. Logs the outcome of the quality check for that
    write - what was submitted, and which warnings, if any, the
    claimant continued past - and, when any were, leaves an INTERNAL
    review note on the claim so the moderator deciding it sees exactly
    what the claimant was told. Returns the note, or None when nothing
    was dismissed.

    Does nothing while enable_claim_name_address_edit is off, matching
    the contribution recording: with the switch off the form never
    shows the fields, so there is nothing to have been warned about.
    The list is not gated on the LLM switch: it only says what the
    claimant saw, and if it is non-empty they saw it.

    The dismissed list comes from the client. It is advisory, capped and
    typed by validate_dismissed_warnings, and only ever read by
    moderators, so trusting it is the right trade against re-running a
    model call (and possibly getting different warnings) on the write.
    '''
    if not switch_is_active(CLAIM_NAME_ADDRESS_EDIT_SWITCH):
        return None

    name = (claim.facility_name_english or '').strip()
    address = (claim.facility_address or '').strip()
    logger.info(
        'Claim quality check outcome: contributor=%s facility=%s claim=%s '
        'source=%s dismissed=%s fields=%s',
        claim.contributor_id,
        claim.facility_id,
        claim.id,
        source,
        [warning['type'] for warning in dismissed_warnings],
        _describe_fields(name, address, claim.facility.country_code),
    )
    if not dismissed_warnings:
        return None

    lines = [
        'Claimant continued past data-quality warnings when '
        f'{_SOURCE_DESCRIPTIONS.get(source, source)}:'
    ]
    for warning in dismissed_warnings:
        line = f'- {WARNING_TITLES[warning["type"]]}'
        if warning.get('message'):
            line += f': {warning["message"]}'
        lines.append(line)
    lines.append(f'Submitted name: {name or "(none)"}')
    lines.append(f'Submitted address: {address or "(none)"}')

    return create_review_note(
        claim,
        acting_user,
        '\n'.join(lines),
        FacilityClaimReviewNoteTypes.INTERNAL,
    )


def _describe_fields(name: str, address: str, country_code) -> str:
    # default=str so an unexpected value type degrades the log line
    # rather than aborting the request.
    return json.dumps(
        {'name': name, 'address': address, 'country': country_code},
        default=str,
    )
