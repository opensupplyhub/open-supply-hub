'''
LLM-backed data-quality verdicts for the name and address a claimant
asserts for a production location (OSDEV-3489). Mirrors the SLC
submission check (SubmissionQualityService) and reuses its four verdicts,
adding one the SLC check has no use for: whether the claimed details
describe a different location from the one currently listed. The claim
form and the claimed-details form both call this through the check
endpoint before the claimant's values are written; see
claim_quality_check_service for the warning mapping and logging.
'''
from typing import Optional

from pydantic import Field

from api.services.submission_quality_service import (
    LLMQualityService,
    QualityVerdict,
    SubmissionQualityVerdicts,
)

# Same override mechanism as SUBMISSION_QUALITY_INSTRUCTIONS, kept
# separate because the framing differs: a claimant correcting the
# listing of a location they operate, not a contributor adding one.
_INSTRUCTIONS_ENV_VAR = 'CLAIM_QUALITY_INSTRUCTIONS'
_DEFAULT_INSTRUCTIONS = (
    'You evaluate the name and address that a person claiming to own or '
    'operate a production facility asserts for it, reporting a verdict '
    'for every check in the output schema. The facility is already '
    'listed with a name and address; the claimant is either confirming '
    'that listing, correcting a stale or wrong listing of the same '
    'facility, or has picked the wrong facility. Flag a check only when '
    'there is a likely problem worth warning the claimant about.'
)


class ClaimQualityVerdicts(SubmissionQualityVerdicts):
    different_location: QualityVerdict = Field(
        description=(
            'Whether the claimed name and address appear to describe a '
            'different production facility from the currently listed '
            'name and address, rather than the same facility with a '
            'corrected or updated name or address. A rename, a '
            'reformatted or more precise address, or a move within the '
            'same area is the same facility; a different company at an '
            'unrelated address in another city or region is not.'
        ),
    )


class ClaimQualityService(LLMQualityService):
    output_type = ClaimQualityVerdicts
    default_instructions = _DEFAULT_INSTRUCTIONS
    instructions_env_var = _INSTRUCTIONS_ENV_VAR
    check_label = 'claim'

    def evaluate(
        self,
        name: str,
        address: str,
        country_name: str,
        current_name: str,
        current_address: str,
    ) -> Optional[ClaimQualityVerdicts]:
        return self._run(
            'Evaluate this production location claim.\n'
            f'Claimed name: {name}\n'
            f'Claimed address: {address}\n'
            f'Country: {country_name}\n'
            f'Currently listed name: {current_name}\n'
            f'Currently listed address: {current_address}'
        )
