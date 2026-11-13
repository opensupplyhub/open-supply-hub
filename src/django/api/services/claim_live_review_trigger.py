'''
Asks the claims automation pipeline to review one claim now
(OSDEV-3804), instead of leaving it for the pipeline's scheduled run.

This is the only place the app reaches out to the pipeline, and it does
one thing: an asynchronous invocation of the pipeline's Lambda function
with the claim id. The call returns as soon as Lambda has accepted the
event; the review itself runs in the pipeline, which reads the claim
and records its decision through the same API it always uses. Nothing
comes back here. The live check learns the outcome from the claim.

The function to call is named by CLAIMS_LIVE_REVIEW_FUNCTION. Empty
means the live check is not configured and nothing is called. Every
failure is caught and reported as "not triggered": the caller tells the
claimant the check is not available, and the claim, which is already
saved, waits for a moderator.
'''
import json
import logging

import boto3
from botocore.config import Config
from django.conf import settings

logger = logging.getLogger(__name__)

# The claimant is waiting on this request, so a slow or unreachable
# Lambda endpoint must not hold it up. No retries: a second attempt
# would only make the wait longer, and the claim is reviewed by the
# scheduled run either way.
TRIGGER_CLIENT_CONFIG = Config(
    connect_timeout=2,
    read_timeout=3,
    retries={'max_attempts': 0},
)

# What Lambda answers when it has queued an asynchronous invocation.
ACCEPTED = 202


def get_live_review_function() -> str:
    return (settings.CLAIMS_LIVE_REVIEW_FUNCTION or '').strip()


def is_live_review_configured() -> bool:
    return bool(get_live_review_function())


def trigger_live_review(claim_id: int) -> bool:
    '''
    Ask the pipeline to review `claim_id` now. True when Lambda accepted
    the request, False when the live check is not configured or the
    request failed for any reason. Never raises.
    '''
    function = get_live_review_function()
    if not function:
        return False

    try:
        response = boto3.client(
            'lambda', config=TRIGGER_CLIENT_CONFIG
        ).invoke(
            FunctionName=function,
            InvocationType='Event',
            Payload=json.dumps({'claim_id': claim_id}).encode(),
        )
        status_code = response.get('StatusCode')
    except Exception:
        logger.exception(
            'Live claim check: the review of claim %s could not be '
            'requested.',
            claim_id,
        )
        return False

    if status_code != ACCEPTED:
        logger.error(
            'Live claim check: the review of claim %s was not accepted '
            '(status %s).',
            claim_id,
            status_code,
        )
        return False
    return True
