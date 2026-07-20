"""Unit tests for :class:`lists_repository.ListsRepository`."""
from __future__ import annotations

from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from lists_repository import (
    CURSOR_LIST_ID,
    STATUS_PENDING,
    ListsRepository,
)


def test_get_last_list_id_missing_cursor():
    table = MagicMock()
    table.get_item.return_value = {}
    repo = ListsRepository(table=table)
    assert repo.get_last_list_id() == 0
    table.get_item.assert_called_once_with(Key={"list_id": CURSOR_LIST_ID})


def test_get_last_list_id_reads_cursor_item():
    table = MagicMock()
    table.get_item.return_value = {
        "Item": {"list_id": CURSOR_LIST_ID, "last_list_id": 42}
    }
    repo = ListsRepository(table=table)
    assert repo.get_last_list_id() == 42


def test_advance_cursor_updates_when_newer():
    table = MagicMock()
    repo = ListsRepository(table=table)
    repo.advance_cursor(99)
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["Key"] == {"list_id": CURSOR_LIST_ID}
    assert kwargs["ExpressionAttributeValues"] == {":new_id": 99}
    assert "last_list_id < :new_id" in kwargs["ConditionExpression"]


def test_advance_cursor_ignores_stale_update():
    table = MagicMock()
    table.update_item.side_effect = ClientError(
        {
            "Error": {
                "Code": "ConditionalCheckFailedException",
                "Message": "stale",
            }
        },
        "UpdateItem",
    )
    repo = ListsRepository(table=table)
    repo.advance_cursor(10)  # does not raise


def test_put_list_writes_expected_item():
    table = MagicMock()
    repo = ListsRepository(table=table)
    written = repo.put_list(
        99,
        list_name="Acme List",
        contributor_id=7,
    )
    assert written is True
    kwargs = table.put_item.call_args.kwargs
    item = kwargs["Item"]
    assert item["list_id"] == "99"
    assert item["contributor_id"] == "7"
    assert item["list_name"] == "Acme List"
    assert item["status"] == STATUS_PENDING
    assert item["started_at"]
    assert item["finished_at"] == ""
    assert kwargs["ConditionExpression"] == "attribute_not_exists(list_id)"


def test_put_list_fills_defaults():
    table = MagicMock()
    repo = ListsRepository(table=table)
    written = repo.put_list(42)
    assert written is True
    item = table.put_item.call_args.kwargs["Item"]
    assert item == {
        "list_id": "42",
        "list_name": "",
        "status": STATUS_PENDING,
        "started_at": item["started_at"],
        "finished_at": "",
    }
    assert item["started_at"]


def test_put_list_skips_existing_item():
    table = MagicMock()
    table.put_item.side_effect = ClientError(
        {
            "Error": {
                "Code": "ConditionalCheckFailedException",
                "Message": "exists",
            }
        },
        "PutItem",
    )
    repo = ListsRepository(table=table)
    written = repo.put_list(1, list_name="Dup")
    assert written is False
