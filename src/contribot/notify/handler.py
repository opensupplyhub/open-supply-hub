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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Error-ratio thresholds for the report mood emoji, from the original ContriBot.
ERROR_RATIO_EMOJIS = [
    (0.05, ":simple_smile:"),
    (0.25, ":confused:"),
]
ERROR_RATIO_FALLBACK_EMOJI = ":disappointed:"


def _base_url() -> str:
    return os.environ["OS_HUB_API_URL"].rstrip("/")


def _error_ratio_line(event: dict) -> str:
    """Return the ``(lines/errors)`` summary line, or "" when stats are absent."""
    num_lines = event.get("num_lines")
    num_errors = event.get("num_errors")
    error_ratio = event.get("error_ratio")
    if num_lines is None or num_errors is None or error_ratio is None:
        return ""

    error_ratio = float(error_ratio)
    emoji = ERROR_RATIO_FALLBACK_EMOJI
    for threshold, threshold_emoji in ERROR_RATIO_EMOJIS:
        if error_ratio < threshold:
            emoji = threshold_emoji
            break
    return f"({num_lines}/{num_errors}) Error ratio: {error_ratio:.1%} {emoji}"


def _contributor_line(base: str, item: dict) -> str:
    """Return the contributor line, or "" when the row has no contributor info."""
    contributor_name = item.get("contributor_name") or ""
    contributor_email = item.get("contributor_email") or ""
    if not (contributor_name or contributor_email):
        return ""

    contributor = f"Contributor {contributor_name}"
    contributor_id = item.get("contributor_id")
    if contributor_id:
        admin_link = f"{base}/admin/api/contributor/{contributor_id}/change/"
        contributor = f"<{admin_link}|{contributor}>"
    return f"{contributor} email {contributor_email}".rstrip()


def _error_line(error: dict | None) -> str:
    """Return the error-cause line, or "" when there is no error."""
    if not error:
        return ""
    cause = error.get("Cause") or error.get("Error") or ""
    return f"Error: {cause[:500]}" if cause else ""


def _build_message(list_id: str, item: dict, event: dict) -> str:
    base = _base_url()
    list_name = item.get("list_name") or event.get("list_name") or ""
    list_link = f"<{base}/lists/{list_id}|#{list_id} {list_name}".rstrip() + ">"
    error = event.get("error")

    headline = (
        f":rotating_light: ContriBot failed to process list {list_link}"
        if error
        else f"New list {list_link}"
    )
    file_name = item.get("file_name") or ""
    report_url = event.get("report_url")

    lines = [
        headline,
        _contributor_line(base, item),
        f"File {file_name}" if file_name else "",
        f"<{report_url}|Checked report>" if report_url else "",
        _error_ratio_line(event),
        _error_line(error),
    ]
    return "\n".join(line for line in lines if line)


def _post_to_slack(message: str, secret_env: str) -> bool:
    """Post ``message`` to the webhook whose secret ARN is in ``secret_env``.

    Returns False instead of raising when the channel is unconfigured or
    Slack is unreachable — a notification problem should not fail the
    workflow after the list was already processed; the message content is
    preserved in the logs.
    """
    secret_arn = os.environ.get(secret_env)
    if not secret_arn:
        logger.info("%s not configured; skipping", secret_env)
        return False

    try:
        SlackWebhook(secret_arn=secret_arn).post(message)
        return True
    except (ClientError, RuntimeError):
        logger.exception("Slack notification via %s failed", secret_env)
        logger.info("Unsent Slack message: %s", json.dumps(message))
        return False


def handler(event, context):
    """Lambda entry point: post a Slack notification for one processed list."""
    list_id = str(event.get("list_id", "unknown"))
    failed = bool(event.get("error"))

    repository = ListsRepository()
    item = repository.get_list(list_id) or {}
    if not item:
        logger.warning("No DynamoDB row for list_id=%s", list_id)

    message = _build_message(list_id, item, event)
    logger.info("Notifying for list_id=%s failed=%s", list_id, failed)

    notified = _post_to_slack(message, "SLACK_API_URL_SECRET_ARN")
    if failed:
        # Failures also go to the failures-only channel so they are not
        # lost in the volume of routine notifications.
        _post_to_slack(message, "SLACK_FAILURES_API_URL_SECRET_ARN")

    repository.finish_list(
        list_id,
        status=STATUS_FAILED if failed else STATUS_PROCESSED,
    )

    return {
        "list_id": list_id,
        "notified": notified,
    }
