"""Notify moderators on Slack after a facility list is processed.

Receives the ``process_list`` output for a single Map item (or the original
item plus ``error`` when processing failed), enriches it with the list row
stored in DynamoDB by ``fetch_lists``, posts a Slack message, and records the
final list status.
"""

from __future__ import annotations

import json
import logging
import os

from botocore.exceptions import ClientError

from lib.lists_repository import (
    STATUS_FAILED,
    STATUS_PROCESSED,
    ListsRepository,
)
from lib.slack_webhook import SlackWebhook
from message import NotifyMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda entry point: post a Slack notification for one processed list."""
    list_id = str(event.get("list_id", "unknown"))
    failed = bool(event.get("error"))

    repository = ListsRepository()
    item = repository.get_list(list_id) or {}
    if not item:
        logger.warning("No DynamoDB row for list_id=%s", list_id)

    notify_message = NotifyMessage(
        list_id=list_id,
        base_url=os.environ["OS_HUB_API_URL"],
        list_name=item.get("list_name") or event.get("list_name") or "",
        contributor_id=item.get("contributor_id"),
        contributor_name=item.get("contributor_name") or "",
        contributor_email=item.get("contributor_email") or "",
        file_name=item.get("file_name") or "",
        report_url=event.get("report_url"),
        num_lines=event.get("num_lines"),
        num_errors=event.get("num_errors"),
        error_ratio=event.get("error_ratio"),
        error=event.get("error"),
    )
    message = notify_message.generate()
    logger.info("Notifying for list_id=%s failed=%s", list_id, failed)

    if failed:
        secret_arn = os.environ["SLACK_FAILURES_API_URL_SECRET_ARN"]
    else:
        secret_arn = os.environ["SLACK_API_URL_SECRET_ARN"]

    notified = False
    try:
        slack_webhook = SlackWebhook(secret_arn=secret_arn)
        slack_webhook.post(message)
        notified = True
    except (ClientError, RuntimeError):
        logger.exception("Slack notification failed")
        logger.info("Unsent Slack message: %s", json.dumps(message))

    repository.update_list(
        list_id,
        status=STATUS_FAILED if failed else STATUS_PROCESSED,
    )

    return {
        "list_id": list_id,
        "notified": notified,
    }
