"""DynamoDB persistence for ContriBot facility-list processing state."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

STATUS_PENDING = "PENDING"
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

    def put_list(
        self,
        list_id: int | str,
        *,
        list_name: str = "",
        contributor_id: Optional[int | str] = None,
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
            "status": status,
            "started_at": started_at or datetime.now(timezone.utc).isoformat(),
            "finished_at": finished_at,
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
