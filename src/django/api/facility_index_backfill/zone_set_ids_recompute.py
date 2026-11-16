"""
Keep `FacilityIndex.zone_set_ids` in step with the zones.

The column is filled by `index_facilities_by` on every facility save,
which covers new facilities and coordinate corrections. Replacing a
set's zones (`ZoneSet.replace_zones`) changes membership for every
location without touching any facility row, so nothing fires; this
module recomputes the column for the whole table then. A full pass
over 2.5M rows takes about a minute against production data, too long
for the admin request, so outside local development it is handed to an
AWS Batch job that runs the `zone_set_ids` group of
`backfill_facility_index` (see `specs.py`); the backfill only writes
the rows whose membership changed.
"""

import io
import logging

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.management.base import OutputWrapper
from django.core.management.color import no_style
from django.db import transaction
from django.utils import timezone

from api.facility_index_backfill.backfill_worker import BackfillWorker
from oar.rollbar import report_error_to_rollbar

log = logging.getLogger(__name__)

FIELD_GROUP = 'zone_set_ids'
BATCH_SIZE = 10000

# The default Batch job definition is sized for list processing (2 vCPUs,
# 4 GB). Each backfill worker is a subprocess of roughly 200 MB, so this
# stays well inside it while splitting the pass over the table.
BATCH_PARALLEL_WORKERS = 4

BATCH_CLIENT_CONFIG = Config(
    connect_timeout=5,
    read_timeout=15,
    retries={'max_attempts': 2},
)

INLINE_RESULT = 'inline'
LOCAL_ENVIRONMENT = 'Local'


def runs_inline():
    """
    Whether the recompute runs in this process rather than on Batch.

    Local development (and the test suite, which runs as it) has no
    Batch queue and a small table, so the pass finishes within the
    request. Every deployed environment has the default queue.
    """
    return settings.ENVIRONMENT == LOCAL_ENVIRONMENT


def backfill_command(parallel):
    """The management command the Batch job runs, as an argv list."""
    return [
        'python', 'manage.py', 'backfill_facility_index',
        '--fields', FIELD_GROUP,
        '--parallel', str(parallel),
        '--batch-size', str(BATCH_SIZE),
    ]


def schedule_zone_set_ids_recompute():
    """
    Recompute `zone_set_ids` for every row once the current transaction
    commits.

    Called by `ZoneSet.replace_zones`. Deferred to commit so the job
    (or the inline pass) sees the new zones, and so a rolled-back
    replacement queues nothing.
    """
    transaction.on_commit(recompute_zone_set_ids)


def recompute_zone_set_ids():
    """
    Run the recompute now (local development) or submit it to AWS Batch.

    Never raises: it runs as an `on_commit` callback after the zones have
    already been committed, so a failure here must not turn into a 500
    for a save that succeeded. The failure is logged and reported to
    Rollbar, and the recovery is to run
    `backfill_facility_index --fields zone_set_ids` by hand.

    Returns:
        The Batch job id, `'inline'` when run in-process, or None when
        the recompute could not be started.
    """
    try:
        if runs_inline():
            _recompute_inline()
            return INLINE_RESULT
        return _submit_batch_job()
    except Exception as exc:  # noqa: BLE001 - see docstring
        log.exception(
            'Could not start the zone_set_ids recompute; zone-set search '
            'results will not reflect the new zones until '
            '`backfill_facility_index --fields zone_set_ids` is run.'
        )
        report_error_to_rollbar(
            message=(
                'Could not start the FacilityIndex.zone_set_ids recompute '
                'after a zone set changed: '
                f'{type(exc).__name__}: {exc}'
            ),
        )
        return None


def _recompute_inline():
    """
    Run the single-worker backfill in this process.

    The worker's progress lines are collected and logged rather than
    written to stdout.
    """
    output = io.StringIO()
    worker = BackfillWorker(OutputWrapper(output), no_style())
    updated = worker.run(
        field_name=FIELD_GROUP,
        worker_id=0,
        workers=1,
        batch_size=BATCH_SIZE,
        dry_run=False,
    )
    log.info(
        'Recomputed zone_set_ids inline: %s rows updated.\n%s',
        updated,
        output.getvalue(),
    )
    return updated


def _submit_batch_job():
    """
    Submit the backfill to the default Batch queue.

    The default job definition runs the list-processing command; the
    container command is overridden so the same image runs
    `backfill_facility_index` instead. The definition's retry strategy
    re-runs a job that fails part-way, which is safe: the backfill only
    rewrites rows whose membership still differs.
    """
    client = boto3.client('batch', config=BATCH_CLIENT_CONFIG)
    job_time = timezone.now().strftime('%Y%m%d-%H%M%S')
    response = client.submit_job(
        jobName=f'zone-set-ids-recompute-{job_time}',
        jobQueue=settings.BATCH_JOB_QUEUE_NAME,
        jobDefinition=settings.BATCH_JOB_DEF_NAME,
        containerOverrides={
            'command': backfill_command(BATCH_PARALLEL_WORKERS),
        },
    )
    job_id = response.get('jobId')
    if not job_id:
        raise RuntimeError(
            f'Batch submit response missing jobId: {response}'
        )
    log.info('Submitted zone_set_ids recompute as Batch job %s.', job_id)
    return job_id
