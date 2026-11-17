"""
How a ListCleaningRun is executed.

`StepFunctionsRunner` starts the `auto-lists-cleaning` state machine
(OSDEV-3724: a deterministic rules pass, then every batch of rows through
the model at once, then one merged result) and later reads its result;
`StubRunner` evaluates local rules synchronously. Both leave ingestion to
`service.ingest_result` so the stored shape is identical.
"""
import json
import logging

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from api.models.facility.list_cleaning_run import ListCleaningRun

log = logging.getLogger(__name__)

# A Step Functions execution input is capped at 256 KB. Rows past this
# size are uploaded to the results bucket's inbox and the execution is
# started with a pointer, which is the one prefix stage 1 reads input from.
INLINE_INPUT_LIMIT = 200 * 1024
INBOX_PREFIX = 'inbox/'

# Both clients are used on the request path (a start at the end of parse,
# a describe on every poll), so a slow AWS answer must not hold a worker.
CLIENT_CONFIG = Config(
    connect_timeout=5,
    read_timeout=20,
    retries={'max_attempts': 2},
)


class RunFailed(Exception):
    pass


class StubRunner:
    name = ListCleaningRun.STUB

    def start(self, run, payload):
        from .stub import run_rules
        from .service import ingest_result
        run.status = ListCleaningRun.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=['status', 'started_at'])
        ingest_result(run, run_rules(payload))

    def fetch_result(self, _run):
        return None


class StepFunctionsRunner:
    name = ListCleaningRun.STEP_FUNCTIONS

    def _client(self, service):
        # A named profile only in local development (see settings); the
        # default chain, which is the task role when deployed, otherwise.
        session = boto3.session.Session(
            profile_name=settings.LIST_CLEANING_AWS_PROFILE)
        return session.client(
            service,
            region_name=settings.LIST_CLEANING_AWS_REGION,
            config=CLIENT_CONFIG,
        )

    @staticmethod
    def _bucket():
        bucket = settings.LIST_CLEANING_RESULTS_BUCKET
        owner = settings.LIST_CLEANING_RESULTS_BUCKET_OWNER
        if not bucket or not owner:
            raise ImproperlyConfigured(
                'LIST_CLEANING_RESULTS_BUCKET and '
                'LIST_CLEANING_RESULTS_BUCKET_OWNER are not both set')
        return bucket, owner

    def _execution_input(self, run, payload):
        body = json.dumps(payload)
        if len(body.encode('utf-8')) <= INLINE_INPUT_LIMIT:
            return body
        bucket, owner = self._bucket()
        key = f'{INBOX_PREFIX}{run.facility_list_id}/run-{run.id}.json'
        self._client('s3').put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(payload['rows']).encode('utf-8'),
            ContentType='application/json',
            ExpectedBucketOwner=owner,
        )
        log.info(f'[List Cleaning] Run {run.id}: {len(payload["rows"])} '
                 f'rows uploaded to s3://{bucket}/{key}')
        return json.dumps({
            'list_id': payload['list_id'],
            'rows_s3': {'bucket': bucket, 'key': key},
        })

    def start(self, run, payload):
        arn = settings.LIST_CLEANING_STATE_MACHINE_ARN
        if not arn:
            raise ImproperlyConfigured(
                'LIST_CLEANING_STATE_MACHINE_ARN is not set')
        response = self._client('stepfunctions').start_execution(
            stateMachineArn=arn,
            name=f'list-{run.facility_list_id}-run-{run.id}',
            input=self._execution_input(run, payload),
        )
        run.execution_arn = response['executionArn']
        run.status = ListCleaningRun.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=['execution_arn', 'status', 'started_at'])

    def fetch_result(self, run):
        """
        Returns the aggregated result once the execution has finished, or
        None while it is still running. Raises RunFailed on failure.

        The aggregate step always writes the result to S3 and returns a
        pointer, {"result_s3": {"bucket", "key"}}, since a long list is
        well over the 256 KB output cap; an inline result is still used
        as-is should a future version return one.
        """
        description = self._client('stepfunctions').describe_execution(
            executionArn=run.execution_arn)
        status = description['status']
        if status == 'RUNNING':
            return None
        if status != 'SUCCEEDED':
            raise RunFailed(
                f'Execution ended with {status}: '
                f'{description.get("error", "")} '
                f'{description.get("cause", "")}'.strip())
        output = json.loads(description.get('output') or '{}')
        pointer = output.get('result_s3')
        if pointer:
            # The bucket must be the one we configured and belong to the
            # account we configured, so a pointer anywhere else is
            # refused whatever the execution output claims.
            bucket, owner = self._bucket()
            if pointer.get('bucket') != bucket:
                raise RunFailed(
                    f'Result pointer names bucket {pointer.get("bucket")!r}, '
                    f'not the configured {bucket!r}')
            body = self._client('s3').get_object(
                Bucket=bucket, Key=pointer['key'],
                ExpectedBucketOwner=owner)['Body'].read()
            output = json.loads(body)
        return output


RUNNERS = {
    ListCleaningRun.STUB: StubRunner,
    ListCleaningRun.STEP_FUNCTIONS: StepFunctionsRunner,
}


def get_runner(name):
    try:
        return RUNNERS[name]()
    except KeyError:
        raise ImproperlyConfigured(f'Unknown list cleaning runner {name!r}')
