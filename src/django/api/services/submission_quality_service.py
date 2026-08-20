import logging
import os
from typing import Optional

import boto3
from botocore.config import Config
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

logger = logging.getLogger(__name__)

BEDROCK_AWS_REGION = os.getenv('BEDROCK_AWS_REGION', 'eu-west-1')
# Unset in production, where the ECS task's IAM role is picked up by the
# default boto3 credential chain. Local dev hardcodes AWS_ACCESS_KEY_ID /
# AWS_SECRET_ACCESS_KEY to MinIO's dummy values for the S3 file-storage
# stand-in (see docker-compose.yml), and those env vars would otherwise
# shadow a developer's real AWS credentials for this call too. Setting
# this to a named profile (e.g. in a local .env file) makes boto3 read
# that profile's credentials instead of the ambient env vars. `or None`
# because .env.sample ships the var set-but-empty, and boto3 would treat
# an empty string as a (nonexistent) profile name rather than "unset".
BEDROCK_AWS_PROFILE = os.getenv('BEDROCK_AWS_PROFILE') or None
# Cross-region inference profile ID, not a bare foundation-model ID - Claude
# Haiku is only invocable in this account/region through an inference
# profile (confirmed by hand against Bedrock in this account). Any Bedrock
# model that supports forced tool use works here, but a non-default value
# must also be granted in the bedrock_invoke_submission_quality_model IAM
# policy (deployment/terraform/iam.tf) or the call will be denied - and
# since this check fails open, that denial is invisible to contributors.
SUBMISSION_QUALITY_MODEL_ID = os.getenv(
    'BEDROCK_SUBMISSION_QUALITY_MODEL_ID',
    'eu.anthropic.claude-haiku-4-5-20251001-v1:0',
)
# This runs synchronously in the same request as duplicate-checking and
# geocoding, so a slow or hung call must not block a legitimate submission.
# Callers treat a timeout the same as any other failure: log it and skip
# the warning (fail open).
INVOKE_TIMEOUT_SECONDS = 5.0

# The system-level framing of the model call - overall task, strictness,
# tone. Overridable per environment so the check can be tuned (e.g. made
# more or less aggressive while watching false-positive rates) with an
# ECS task-definition change rather than a release. Read when the agent
# is first built (lazily, on the first evaluate() call), not at module
# import, so a change takes effect on restart and tests can patch the
# environment. What each check MEANS deliberately
# stays in the Field descriptions on SubmissionQualityVerdicts below:
# those are structurally coupled to the output schema and to the
# processor's warning mapping, so making them config would let prompt
# text drift out of sync with the code that consumes the verdicts.
_INSTRUCTIONS_ENV_VAR = 'SUBMISSION_QUALITY_INSTRUCTIONS'
_DEFAULT_INSTRUCTIONS = (
    'You evaluate a single-location production facility contribution for '
    'data-quality problems, reporting a verdict for every check in the '
    'output schema. Flag a check only when there is a likely problem '
    'worth warning the contributor about.'
)


class QualityVerdict(BaseModel):
    flagged: bool = Field(
        description=(
            'true if this check found a likely problem worth warning the '
            'contributor about, false otherwise.'
        ),
    )
    reason: str = Field(
        description=(
            'A short, one-sentence explanation shown to the contributor '
            'when flagged is true. Empty string when flagged is false.'
        ),
    )


class SubmissionQualityVerdicts(BaseModel):
    name_quality: QualityVerdict = Field(
        description=(
            'Whether the submitted name looks like a plausible '
            'facility/business name, as opposed to test data, a '
            "person's name, or gibberish."
        ),
    )
    address_quality: QualityVerdict = Field(
        description=(
            'Whether the submitted address looks like a real, '
            'sufficiently specific facility address - it should '
            'ideally include a street name/number and either a '
            'city/municipality or a state/province, not just a '
            'country or a vague area.'
        ),
    )
    address_country_mismatch: QualityVerdict = Field(
        description=(
            'Whether the submitted address appears inconsistent with '
            '(does not match) the submitted country. flagged should '
            'be true when the address looks like it does NOT match.'
        ),
    )
    multiple_locations: QualityVerdict = Field(
        description=(
            'Whether the name or address appears to describe more '
            'than one distinct facility, e.g. two names or two '
            'addresses joined together.'
        ),
    )


class SubmissionQualityService:
    '''
    Evaluates all AI-judgable SLC submission quality checks (name quality,
    address quality/specificity, address-country match, multiple locations
    bundled into one submission) in a single LLM call, so adding another
    AI-judgable check later only means adding a field to
    SubmissionQualityVerdicts.

    The call goes through pydantic-ai, which is model- and
    vendor-independent: the output schema, instructions, and everything
    the callers see are defined against pydantic-ai's Agent, and only the
    model construction below is Bedrock-specific (chosen because Bedrock
    authenticates with the ECS task's IAM role - no API key to manage).
    Swapping the model is a config change (see
    BEDROCK_SUBMISSION_QUALITY_MODEL_ID above); swapping the provider
    means replacing the BedrockConverseModel construction only.

    Fails open: any error building the underlying bedrock client or
    agent, any error or timeout during the call, and any output that does
    not validate against the schema is logged and returns None so the
    caller skips the warning rather than blocking a legitimate
    submission.
    '''

    def __init__(self):
        # No client or agent is built here: the contribution pipeline
        # constructs this service for every contribution request -
        # including API and PATCH requests the check never evaluates -
        # so construction must be free and must have no failure modes.
        # See _get_agent.
        self._agent: Optional[Agent] = None

    def _get_agent(self) -> Agent:
        # Built lazily on first use rather than in __init__, so that a
        # construction error (e.g. a misconfigured BEDROCK_AWS_PROFILE
        # raising ProfileNotFound when the client resolves the profile)
        # lands in evaluate()'s fail-open handler instead of escaping
        # while the contribution pipeline is being assembled and
        # aborting the submission - and so requests that never invoke
        # the check skip the boto3 session/client construction entirely.
        if self._agent is None:
            bedrock_client = boto3.session.Session(
                profile_name=BEDROCK_AWS_PROFILE,
            ).client(
                'bedrock-runtime',
                region_name=BEDROCK_AWS_REGION,
                config=Config(
                    connect_timeout=INVOKE_TIMEOUT_SECONDS,
                    read_timeout=INVOKE_TIMEOUT_SECONDS,
                    # One attempt total: boto3's default retries would
                    # stack on top of the timeout and block the
                    # submission request.
                    retries={'max_attempts': 1},
                ),
            )
            self._agent = Agent(
                BedrockConverseModel(
                    SUBMISSION_QUALITY_MODEL_ID,
                    provider=BedrockProvider(bedrock_client=bedrock_client),
                ),
                output_type=SubmissionQualityVerdicts,
                # `or` rather than a getenv default: .env.sample ships
                # the var set-but-empty, which must mean "use the
                # default" too.
                instructions=(
                    os.getenv(_INSTRUCTIONS_ENV_VAR) or _DEFAULT_INSTRUCTIONS
                ),
                # No re-prompting on output that fails schema validation
                # - a retry is a second synchronous model call in the
                # request path. An invalid output raises instead, and
                # evaluate() fails open.
                retries=0,
            )
        return self._agent

    def evaluate(
        self, name: str, address: str, country_name: str
    ) -> Optional[SubmissionQualityVerdicts]:
        try:
            result = self._get_agent().run_sync(
                'Evaluate this production location submission.\n'
                f'Name: {name}\n'
                f'Address: {address}\n'
                f'Country: {country_name}'
            )
        except Exception:
            logger.exception(
                'Submission quality check failed; skipping (fail open).'
            )
            return None

        # Separate try block: a failure reading usage must not discard a
        # verdict the model already produced.
        try:
            usage = result.usage
            logger.info(
                'Submission quality check tokens: input=%s output=%s',
                usage.input_tokens,
                usage.output_tokens,
            )
        except Exception:
            logger.warning(
                'Submission quality check succeeded but token usage '
                'could not be read.',
                exc_info=True,
            )

        return result.output
