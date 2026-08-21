"""Re-enqueue FAILED facility lists and start the ContriBot Map.

Scans DynamoDB for ``FAILED`` rows under the attempt cap, resets them to
``PENDING``, and starts the existing Step Functions workflow with those
``list_id``s so ``fetch_lists`` (and the API cursor) is skipped.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import boto3

from lib.lists_repository import STATUS_FAILED, STATUS_PENDING, ListsRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda entry point: retry FAILED lists via a new state-machine execution."""
    repository = ListsRepository()
    max_attempts = int(os.environ.get("CONTRIBOT_MAX_ATTEMPTS", "3"))
    failed_items = repository.scan(
        status=STATUS_FAILED,
        max_attempts=max_attempts,
    )
    logger.info("Scanned %s FAILED list(s) under attempt cap", len(failed_items))

    lists: list[dict[str, str]] = []
    now = datetime.now(timezone.utc).isoformat()
    for item in failed_items:
        list_id = str(item["list_id"])
        repository.update_list(
            list_id,
            status=STATUS_PENDING,
            attempt_count=int(item.get("attempt_count") or 0) + 1,
            started_at=now,
            finished_at="",
        )
        lists.append({"list_id": list_id})

    if not lists:
        logger.info("No FAILED lists to retry")
        return

    logger.info("Starting retry execution for %s list(s)", len(lists))
    return boto3.client("stepfunctions").start_execution(
        stateMachineArn=os.environ["CONTRIBOT_STATE_MACHINE_ARN"],
        input=json.dumps({"lists": lists}),
    )
