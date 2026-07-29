"""DynamoDB persistence for ContriBot facility-list processing state."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

STATUS_PENDING = "PENDING"
STATUS_PROCESSING = "PROCESSING"
STATUS_PROCESSED = "PROCESSED"
STATUS_FAILED = "FAILED"
# Reserved hash-key item that stores the id__gt watermark (not a facility list).
CURSOR_LIST_ID = "__CURSOR__"


class ListsRepository:
    """Read/write facility-list state and the resume cursor in DynamoDB."""

    def __init__(
        self,
        table_name: Optional[str] = None,
        dynamodb_resource: Optional[Any] = None,
        table: Optional[Any] = None,
    ):
        if table is not None:
            self._table = table
            return

        name = table_name or os.environ["CONTRIBOT_STATE_TABLE_NAME"]
        resource = dynamodb_resource or boto3.resource("dynamodb")
        self._table = resource.Table(name)

    def _last_list_id_from_env(self) -> int:
        """Return ``LAST_LIST_ID`` from the environment."""
        raw = os.environ["LAST_LIST_ID"]
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid LAST_LIST_ID={raw!r}") from exc

    def get_last_list_id(self) -> int:
        """Return the resume cursor from the ``__CURSOR__`` item, or ``LAST_LIST_ID``.

        When the cursor item is missing or invalid, falls back to the
        ``LAST_LIST_ID`` environment variable so runs can resume from a configured
        watermark without reprocessing from the beginning.

        O(1) ``GetItem`` — avoids scanning every enqueued facility-list row.
        """
        response = self._table.get_item(Key={"list_id": CURSOR_LIST_ID})
        item = response.get("Item") or {}
        last_list_id = item.get("last_list_id")
        if last_list_id is None:
            return self._last_list_id_from_env()

        try:
            return int(last_list_id)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid cursor last_list_id=%r; falling back to LAST_LIST_ID",
                last_list_id,
            )
            return self._last_list_id_from_env()

    def advance_cursor(self, list_id: int) -> None:
        """Advance the watermark when ``list_id`` is greater than the stored value.

        Uses a conditional update so concurrent runs only move the cursor forward.
        """
        try:
            self._table.update_item(
                Key={"list_id": CURSOR_LIST_ID},
                UpdateExpression="SET last_list_id = :new_id",
                ConditionExpression=(
                    "attribute_not_exists(last_list_id) OR last_list_id < :new_id"
                ),
                ExpressionAttributeValues={":new_id": list_id},
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.info(
                    "Cursor already at or past list_id=%s; leaving unchanged",
                    list_id,
                )
                return
            raise

    def get_list(self, list_id: int | str) -> Optional[dict[str, Any]]:
        """Return the facility-list row for ``list_id``, or None when absent."""
        response = self._table.get_item(Key={"list_id": str(list_id)})
        return response.get("Item")

    def update_list(
        self,
        list_id: int | str,
        *,
        status: Optional[str] = None,
        report_url: Optional[str] = None,
        num_lines: Optional[int] = None,
        num_errors: Optional[int] = None,
        error_ratio: Optional[float] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        attempt_count: Optional[int] = None,
    ) -> None:
        """Update provided fields on a facility-list row.

        Only non-``None`` keyword arguments are written. When ``status`` is
        ``PROCESSED`` or ``FAILED`` and ``finished_at`` is omitted, ``finished_at``
        is set to the current UTC timestamp.
        """
        values: dict[str, Any] = {}
        names: dict[str, str] = {}
        assignments: list[str] = []

        if status is not None:
            names["#status"] = "status"
            values[":status"] = status
            assignments.append("#status = :status")
            if finished_at is None and status in (
                STATUS_PROCESSED,
                STATUS_FAILED,
            ):
                finished_at = datetime.now(timezone.utc).isoformat()

        if report_url is not None:
            values[":report_url"] = report_url
            assignments.append("report_url = :report_url")

        if num_lines is not None:
            values[":num_lines"] = num_lines
            assignments.append("num_lines = :num_lines")

        if num_errors is not None:
            values[":num_errors"] = num_errors
            assignments.append("num_errors = :num_errors")

        if error_ratio is not None:
            values[":error_ratio"] = Decimal(str(error_ratio))
            assignments.append("error_ratio = :error_ratio")

        if started_at is not None:
            values[":started_at"] = started_at
            assignments.append("started_at = :started_at")

        if attempt_count is not None:
            values[":attempt_count"] = attempt_count
            assignments.append("attempt_count = :attempt_count")

        if finished_at is not None:
            values[":finished_at"] = finished_at
            assignments.append("finished_at = :finished_at")

        if not assignments:
            raise ValueError("update_list requires at least one field to update")

        kwargs: dict[str, Any] = {
            "Key": {"list_id": str(list_id)},
            "UpdateExpression": "SET " + ", ".join(assignments),
            "ExpressionAttributeValues": values,
        }
        if names:
            kwargs["ExpressionAttributeNames"] = names
        self._table.update_item(**kwargs)

    def finish_list(self, list_id: int | str, *, status: str) -> None:
        """Set the final ``status`` and ``finished_at`` timestamp for a list row."""
        self._table.update_item(
            Key={"list_id": str(list_id)},
            UpdateExpression="SET #status = :status, finished_at = :finished_at",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": status,
                ":finished_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def put_list(
        self,
        list_id: int | str,
        *,
        list_name: str = "",
        contributor_id: Optional[int | str] = None,
        contributor_name: str = "",
        contributor_email: str = "",
        file_name: str = "",
        status: str = STATUS_PENDING,
        started_at: Optional[str] = None,
        finished_at: str = "",
    ) -> bool:
        """Insert a facility-list row in DynamoDB.

        Missing optional fields are filled with defaults (``PENDING`` status,
        current UTC timestamp for ``started_at``, empty ``finished_at``).

        Returns True when the item was written, False when it already existed.
        """
        item: dict[str, Any] = {
            "list_id": str(list_id),
            "list_name": list_name,
            "contributor_name": contributor_name,
            "contributor_email": contributor_email,
            "file_name": file_name,
            "status": status,
            "started_at": started_at or datetime.now(timezone.utc).isoformat(),
            "finished_at": finished_at,
            "attempt_count": 0,
        }
        if contributor_id is not None:
            item["contributor_id"] = str(contributor_id)

        try:
            self._table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(list_id)",
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.info("List %s already enqueued; skipping PutItem", list_id)
                return False
            raise

    def scan(
        self,
        status: str,
        max_attempts: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Paginated table scan filtered by ``status``.

        When ``max_attempts`` is set, rows with ``attempt_count`` at or above
        that value are excluded (missing ``attempt_count`` counts as 0).
        """
        scan_args: dict[str, Any] = {
            "ExpressionAttributeNames": {"#status": "status"},
            "ExpressionAttributeValues": {":status": status},
        }
        conditions = ["#status = :status"]
        if max_attempts is not None:
            conditions.append(
                "(attribute_not_exists(attempt_count) OR attempt_count < :max_attempts)"
            )
            scan_args["ExpressionAttributeValues"][":max_attempts"] = max_attempts
        scan_args["FilterExpression"] = " AND ".join(conditions)
        items: list[dict[str, Any]] = []

        while True:
            response = self._table.scan(**scan_args)
            items.extend(response.get("Items") or [])
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            scan_args["ExclusiveStartKey"] = last_key

        return items
