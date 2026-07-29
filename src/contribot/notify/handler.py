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


def _build_message(list_id: str, item: dict, event: dict) -> str:
    base = _base_url()
    list_name = item.get("list_name") or event.get("list_name") or ""
    list_link = f"<{base}/lists/{list_id}|#{list_id} {list_name}".rstrip() + ">"

    lines = []
    error = event.get("error")
    if error:
        lines.append(f":rotating_light: ContriBot failed to process list {list_link}")
    else:
        lines.append(f"New list {list_link}")

    contributor_name = item.get("contributor_name") or ""
    contributor_email = item.get("contributor_email") or ""
    contributor_id = item.get("contributor_id")
    if contributor_name or contributor_email:
        if contributor_id:
            admin_link = f"{base}/admin/api/contributor/{contributor_id}/change/"
            contributor = f"<{admin_link}|Contributor {contributor_name}>"
        else:
            contributor = f"Contributor {contributor_name}"
        lines.append(f"{contributor} email {contributor_email}".rstrip())

    file_name = item.get("file_name") or ""
    if file_name:
        lines.append(f"File {file_name}")

    report_url = event.get("report_url")
    if report_url:
        lines.append(f"<{report_url}|Checked report>")

    ratio_line = _error_ratio_line(event)
    if ratio_line:
        lines.append(ratio_line)

    if error:
        cause = error.get("Cause") or error.get("Error") or ""
        if cause:
            lines.append(f"Error: {cause[:500]}")

    return "\n".join(lines)


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

    try:
        SlackWebhook().post(message)
        notified = True
    except RuntimeError:
        # A Slack outage should not fail the workflow after the list was
        # already processed; the message content is preserved in the logs.
        logger.exception("Slack notification failed for list_id=%s", list_id)
        logger.info("Unsent Slack message: %s", json.dumps(message))
        notified = False

    repository.finish_list(
        list_id,
        status=STATUS_FAILED if failed else STATUS_PROCESSED,
    )

    return {
        "list_id": list_id,
        "notified": notified,
    }
