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
- Dismissed warnings are recorded (OSDEV-3537). SLC stores nothing
  because no one reviews an approved SLC by hand; a claim is decided by
  a moderator, so the write endpoints accept the warnings the claimant
  continued past and leave an INTERNAL review note listing them.

Everything here is advisory and fails open: the claimant is never
blocked, and any failure of the model call means no warnings.
'''
import json
import logging
import re
from typing import Dict, List, Optional

from waffle import switch_is_active

from api.models.facility.facility import Facility
from api.services.claim_contribution_service import (
    CLAIM_NAME_ADDRESS_EDIT_SWITCH,
)
from api.services.claim_quality_service import ClaimQualityService
from api.services.claim_quality_warnings import WARNING_TITLES
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

_WHITESPACE = re.compile(r'\s+')


def is_claim_quality_check_active() -> bool:
    return (
        switch_is_active(CLAIM_NAME_ADDRESS_EDIT_SWITCH)
        and switch_is_active(CLAIM_QUALITY_CHECK_SWITCH)
    )


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

    Every evaluated pair logs one INFO line carrying the judged fields,
    so that what the check saw can be compared with what was later
    submitted (the write endpoints' outcome line, OSDEV-3537). Only the name,
    address and country are logged: they are what the model judges and the
    published record of a location anyway. Nothing else in the request
    reaches the log.
    '''
    if not is_claim_quality_check_active():
        return []

    name = (name or '').strip()
    address = (address or '').strip()
    current_name = facility.name or ''
    current_address = facility.address or ''
    if (
        _same_value(name, current_name)
        and _same_value(address, current_address)
    ):
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
        current_name=current_name,
        current_address=current_address,
    )

    warnings = []
    if verdicts is not None:
        for warning_type, title in WARNING_TITLES.items():
            verdict = getattr(verdicts, warning_type)
            if verdict.flagged:
                warnings.append({
                    'type': warning_type,
                    'title': title,
                    'message': verdict.reason,
                })

    # Logged whether or not anything was flagged (and even when the
    # model call failed, with an empty list), so that every evaluated
    # pair has a line to compare against the outcome line of the write
    # that follows, if any.
    logger.info(
        'Claim quality check evaluated: contributor=%s facility=%s '
        'warnings=%s fields=%s',
        contributor_id,
        facility.id,
        [warning['type'] for warning in warnings],
        _describe_fields(name, address, country_code),
    )
    return warnings


def _same_value(left: str, right: str) -> bool:
    return (
        _WHITESPACE.sub(' ', left).strip().casefold()
        == _WHITESPACE.sub(' ', right).strip().casefold()
    )


def _describe_fields(name: str, address: str, country_code) -> str:
    # default=str so an unexpected value type degrades the log line
    # rather than aborting the request.
    return json.dumps(
        {'name': name, 'address': address, 'country': country_code},
        default=str,
    )
