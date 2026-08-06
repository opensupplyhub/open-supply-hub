import logging
import os
from dataclasses import dataclass
from typing import Optional

from anthropic import AnthropicBedrock

logger = logging.getLogger(__name__)

BEDROCK_AWS_REGION = os.getenv('BEDROCK_AWS_REGION', 'eu-west-1')
# Unset in production, where the ECS task's IAM role is picked up by the
# default boto3 credential chain. Local dev hardcodes AWS_ACCESS_KEY_ID /
# AWS_SECRET_ACCESS_KEY to MinIO's dummy values for the S3 file-storage
# stand-in (see docker-compose.yml), and those env vars would otherwise
# shadow a developer's real AWS credentials for this call too. Setting
# this to a named profile (e.g. in a local .env file) makes boto3 read
# that profile's credentials instead of the ambient env vars.
BEDROCK_AWS_PROFILE = os.getenv('BEDROCK_AWS_PROFILE')
# Cross-region inference profile ID, not a bare foundation-model ID - Claude
# Haiku is only invocable in this account/region through an inference
# profile (confirmed by hand against Bedrock in this account).
SUBMISSION_QUALITY_MODEL_ID = os.getenv(
    'BEDROCK_SUBMISSION_QUALITY_MODEL_ID',
    'eu.anthropic.claude-haiku-4-5-20251001-v1:0',
)
# This runs synchronously in the same request as duplicate-checking and
# geocoding, so a slow or hung call must not block a legitimate submission.
# Callers treat a timeout the same as any other failure: log it and skip
# the warning (fail open).
INVOKE_TIMEOUT_SECONDS = 5.0

_TOOL_NAME = 'submission_quality_check'


def _verdict_property(description: str) -> dict:
    return {
        'type': 'object',
        'description': description,
        'properties': {
            'flagged': {
                'type': 'boolean',
                'description': (
                    'true if this check found a likely problem worth '
                    'warning the contributor about, false otherwise.'
                ),
            },
            'reason': {
                'type': 'string',
                'description': (
                    'A short, one-sentence explanation shown to the '
                    'contributor when flagged is true. Empty string when '
                    'flagged is false.'
                ),
            },
        },
        'required': ['flagged', 'reason'],
    }


_TOOL_SCHEMA = {
    'name': _TOOL_NAME,
    'description': (
        'Report data-quality verdicts for a single-location production '
        'facility contribution.'
    ),
    'input_schema': {
        'type': 'object',
        'properties': {
            'name_quality': _verdict_property(
                'Whether the submitted name looks like a plausible '
                'facility/business name, as opposed to test data, a '
                "person's name, or gibberish."
            ),
            'address_quality': _verdict_property(
                'Whether the submitted address looks like a real, '
                'sufficiently specific facility address - it should '
                'ideally include a street name/number and either a '
                'city/municipality or a state/province, not just a '
                'country or a vague area.'
            ),
            'address_country_mismatch': _verdict_property(
                'Whether the submitted address appears inconsistent with '
                '(does not match) the submitted country. flagged should '
                'be true when the address looks like it does NOT match.'
            ),
            'multiple_locations': _verdict_property(
                'Whether the name or address appears to describe more '
                'than one distinct facility, e.g. two names or two '
                'addresses joined together.'
            ),
        },
        'required': [
            'name_quality',
            'address_quality',
            'address_country_mismatch',
            'multiple_locations',
        ],
    },
}


@dataclass(frozen=True)
class QualityVerdict:
    flagged: bool
    reason: str


@dataclass(frozen=True)
class SubmissionQualityVerdicts:
    name_quality: QualityVerdict
    address_quality: QualityVerdict
    address_country_mismatch: QualityVerdict
    multiple_locations: QualityVerdict


class SubmissionQualityService:
    '''
    Evaluates all AI-judgable SLC submission quality checks (name quality,
    address quality/specificity, address-country match, multiple locations
    bundled into one submission) in a single Bedrock-hosted Claude call,
    using forced tool-use for structured output - one round trip per
    submission rather than one model call per check, so adding another
    AI-judgable check later only means adding a field to this schema.

    Fails open: any error, timeout, or unexpected response shape is logged
    and returns None so the caller skips the warning rather than blocking
    a legitimate submission.
    '''

    def __init__(self):
        self._client = AnthropicBedrock(
            aws_region=BEDROCK_AWS_REGION,
            aws_profile=BEDROCK_AWS_PROFILE,
        )

    def evaluate(
        self, name: str, address: str, country_name: str
    ) -> Optional[SubmissionQualityVerdicts]:
        try:
            response = self._client.messages.create(
                model=SUBMISSION_QUALITY_MODEL_ID,
                max_tokens=1024,
                tools=[_TOOL_SCHEMA],
                tool_choice={'type': 'tool', 'name': _TOOL_NAME},
                messages=[{
                    'role': 'user',
                    'content': (
                        'Evaluate this production location submission.\n'
                        f'Name: {name}\n'
                        f'Address: {address}\n'
                        f'Country: {country_name}'
                    ),
                }],
                timeout=INVOKE_TIMEOUT_SECONDS,
            )
        except Exception:
            logger.exception(
                'Submission quality check failed; skipping (fail open).'
            )
            return None

        return self.__parse_response(response)

    @staticmethod
    def __parse_response(response) -> Optional[SubmissionQualityVerdicts]:
        tool_use = next(
            (block for block in response.content
             if block.type == 'tool_use'),
            None,
        )
        if tool_use is None:
            logger.error(
                'Submission quality check returned no tool_use block; '
                'skipping (fail open).'
            )
            return None

        try:
            data = tool_use.input
            return SubmissionQualityVerdicts(
                name_quality=QualityVerdict(**data['name_quality']),
                address_quality=QualityVerdict(**data['address_quality']),
                address_country_mismatch=QualityVerdict(
                    **data['address_country_mismatch']
                ),
                multiple_locations=QualityVerdict(
                    **data['multiple_locations']
                ),
            )
        except (KeyError, TypeError):
            logger.exception(
                'Submission quality check returned an unexpected shape; '
                'skipping (fail open).'
            )
            return None
