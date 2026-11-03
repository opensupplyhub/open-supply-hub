"""
How a ListCleaningRun is executed.

`StepFunctionsRunner` starts the OSDEV-3724 state machine and later reads
its result; `StubRunner` evaluates local rules synchronously. Both leave
ingestion to `service.ingest_result` so the stored shape is identical.
"""
import json
import logging

import boto3
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from api.models.facility.list_cleaning_run import ListCleaningRun

log = logging.getLogger(__name__)


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

    def fetch_result(self, run):
        return None


class StepFunctionsRunner:
    name = ListCleaningRun.STEP_FUNCTIONS

    def _client(self):
        return boto3.client(
            'stepfunctions', region_name=settings.LIST_CLEANING_AWS_REGION)

    def start(self, run, payload):
        arn = settings.LIST_CLEANING_STATE_MACHINE_ARN
        if not arn:
            raise ImproperlyConfigured(
                'LIST_CLEANING_STATE_MACHINE_ARN is not set')
        response = self._client().start_execution(
            stateMachineArn=arn,
            name=f'list-{run.facility_list_id}-run-{run.id}',
            input=json.dumps(payload),
        )
        run.execution_arn = response['executionArn']
        run.status = ListCleaningRun.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=['execution_arn', 'status', 'started_at'])

    def fetch_result(self, run):
        """
        Returns the aggregated result once the execution has finished, or
        None while it is still running. Raises RunFailed on failure.

        OSDEV-3724 has not yet decided whether the aggregate is returned
        inline or written to S3 (inline is capped at 256 KB). Both are
        handled: an inline result is used as-is, and an output of the form
        {"result_s3": {"bucket": ..., "key": ...}} is fetched.
        """
        description = self._client().describe_execution(
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
            s3 = boto3.client(
                's3', region_name=settings.LIST_CLEANING_AWS_REGION)
            body = s3.get_object(
                Bucket=pointer['bucket'], Key=pointer['key'])['Body'].read()
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
