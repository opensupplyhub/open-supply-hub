"""Monday.com GraphQL client for ContriBot approval-queue items."""

from __future__ import annotations

import json
import os
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3

# Title aliases on the Contributor List Approval Queue (and copies of it).
COLUMN_TITLES = {
    "contributor_name": ("Contributor Name", "contributor name"),
    "contributor_id": ("Contributor ID", "contributor id"),
    "processed_data": ("Processed Data", "Processed Data Drive"),
    "os_hub_link": (
        "OS Hub List Link",
        "OS Hub Link",
        "OS Hub list link",
        "OS Hub",
    ),
    "list_size": ("List Size", "list size"),
}


class MondayBoard:
    """Create items on the ContriBot Monday approval-queue board.

    The API token is read from Secrets Manager (``MONDAY_API_KEY_SECRET_ARN``).
    Column IDs are resolved from the board by title so they are not hardcoded.
    """

    def __init__(
        self,
        *,
        api_url: Optional[str] = None,
        board_id: Optional[str] = None,
        secret_arn: Optional[str] = None,
        secrets_client: Optional[Any] = None,
        token: Optional[str] = None,
    ):
        self._api_url = (api_url or os.environ["MONDAY_API_URL"]).rstrip("/")
        raw_board_id = board_id if board_id is not None else os.environ.get(
            "MONDAY_BOARD_ID", ""
        )
        self._board_id = str(raw_board_id).strip()
        if not self._board_id:
            raise RuntimeError("MONDAY_BOARD_ID is not configured")

        if token is not None:
            self._token = token
        else:
            arn = secret_arn or os.environ["MONDAY_API_KEY_SECRET_ARN"]
            client = secrets_client or boto3.client("secretsmanager")
            response = client.get_secret_value(SecretId=arn)
            if "SecretString" not in response:
                raise RuntimeError(f"Secret {arn} has no SecretString")
            self._token = response["SecretString"].strip()

        self._columns: Optional[list[dict[str, Any]]] = None

    def create_item(
        self,
        *,
        item_name: str,
        contributor_name: str = "",
        contributor_id: Optional[str] = None,
        processed_url: Optional[str] = None,
        os_hub_url: Optional[str] = None,
        list_size: Optional[int] = None,
    ) -> str:
        """Create an approval-queue item and return its Monday item id."""
        columns = self._column_map()
        values: dict[str, Any] = {}

        self._set_text(values, columns, "contributor_name", contributor_name)
        if contributor_id is not None and str(contributor_id):
            self._set_text(values, columns, "contributor_id", str(contributor_id))
        if processed_url:
            self._set_link(values, columns, "processed_data", processed_url)
        if os_hub_url:
            self._set_link(values, columns, "os_hub_link", os_hub_url)
        if list_size is not None:
            self._set_number(values, columns, "list_size", list_size)

        payload = self._graphql(
            """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
              create_item(
                board_id: $boardId
                item_name: $itemName
                column_values: $columnValues
              ) { id }
            }
            """,
            {
                "boardId": self._board_id,
                "itemName": item_name,
                "columnValues": json.dumps(values),
            },
        )
        item_id = ((payload.get("data") or {}).get("create_item") or {}).get("id")
        if not item_id:
            raise RuntimeError(f"Monday create_item returned no id: {payload}")
        return str(item_id)

    def _column_map(self) -> dict[str, dict[str, Any]]:
        """Return semantic-key -> {id, type} for known column titles."""
        if self._columns is None:
            payload = self._graphql(
                """
                query ($boardIds: [ID!]) {
                  boards(ids: $boardIds) { columns { id title type } }
                }
                """,
                {"boardIds": [self._board_id]},
            )
            boards = (payload.get("data") or {}).get("boards") or []
            if not boards:
                raise RuntimeError(
                    f"Monday board {self._board_id} was not found or has no columns"
                )
            self._columns = boards[0].get("columns") or []

        by_title = {
            (column.get("title") or "").strip().lower(): column
            for column in self._columns
        }
        mapped: dict[str, dict[str, Any]] = {}
        for key, titles in COLUMN_TITLES.items():
            for title in titles:
                column = by_title.get(title.lower())
                if column and column.get("id"):
                    mapped[key] = column
                    break
        return mapped

    def _set_text(
        self,
        values: dict[str, Any],
        columns: dict[str, dict[str, Any]],
        key: str,
        text: str,
    ) -> None:
        if not text:
            return
        column = columns.get(key)
        if column:
            values[column["id"]] = text

    def _set_link(
        self,
        values: dict[str, Any],
        columns: dict[str, dict[str, Any]],
        key: str,
        url: str,
    ) -> None:
        column = columns.get(key)
        if not column:
            return
        if column.get("type") == "link":
            values[column["id"]] = {"url": url, "text": url}
        else:
            values[column["id"]] = url

    def _set_number(
        self,
        values: dict[str, Any],
        columns: dict[str, dict[str, Any]],
        key: str,
        number: int,
    ) -> None:
        column = columns.get(key)
        if column:
            values[column["id"]] = str(number)

    def _graphql(
        self, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        request = Request(
            self._api_url,
            data=json.dumps({"query": query, "variables": variables}).encode(
                "utf-8"
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": self._token,
                "API-Version": "2024-10",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Monday API request failed ({exc.code}): {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Monday API request failed: {exc}") from exc

        payload = json.loads(body)
        errors = payload.get("errors")
        if errors:
            raise RuntimeError(f"Monday GraphQL errors: {errors}")
        return payload
