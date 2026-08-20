"""Unit tests for :class:`lists_repository.ListsRepository`."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from lists_repository import (
    CURSOR_LIST_ID,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_PROCESSED,
    STATUS_PROCESSING,
    ListsRepository,
)


def test_get_last_list_id_missing_cursor_raises_when_last_list_id_unset():
    table = MagicMock()
    table.get_item.return_value = {}
    repo = ListsRepository(table=table)
    with pytest.raises(KeyError, match="LAST_LIST_ID"):
        repo.get_last_list_id()
    table.get_item.assert_called_once_with(Key={"list_id": CURSOR_LIST_ID})


def test_get_last_list_id_missing_cursor_uses_last_list_id_env(monkeypatch):
    monkeypatch.setenv("LAST_LIST_ID", "500")
    table = MagicMock()
    table.get_item.return_value = {}
    repo = ListsRepository(table=table)
    assert repo.get_last_list_id() == 500


def test_get_last_list_id_invalid_cursor_uses_last_list_id_env(monkeypatch):
    monkeypatch.setenv("LAST_LIST_ID", "250")
    table = MagicMock()
    table.get_item.return_value = {
        "Item": {"list_id": CURSOR_LIST_ID, "last_list_id": "not-a-number"}
    }
    repo = ListsRepository(table=table)
    assert repo.get_last_list_id() == 250


def test_last_list_id_from_env_raises_for_invalid_value(monkeypatch):
    monkeypatch.setenv("LAST_LIST_ID", "not-a-number")
    repo = ListsRepository(table=MagicMock())
    with pytest.raises(ValueError, match="Invalid LAST_LIST_ID"):
        repo._last_list_id_from_env()


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
        contributor_name="Acme Corp",
        contributor_email="admin@acme.com",
        file_name="acme.csv",
    )
    assert written is True
    kwargs = table.put_item.call_args.kwargs
    item = kwargs["Item"]
    assert item["list_id"] == "99"
    assert item["contributor_id"] == "7"
    assert item["list_name"] == "Acme List"
    assert item["contributor_name"] == "Acme Corp"
    assert item["contributor_email"] == "admin@acme.com"
    assert item["file_name"] == "acme.csv"
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
        "contributor_name": "",
        "contributor_email": "",
        "file_name": "",
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


def test_get_list_returns_item():
    table = MagicMock()
    table.get_item.return_value = {"Item": {"list_id": "7", "status": STATUS_PENDING}}
    repo = ListsRepository(table=table)
    assert repo.get_list(7) == {"list_id": "7", "status": STATUS_PENDING}
    table.get_item.assert_called_once_with(Key={"list_id": "7"})


def test_get_list_returns_none_when_missing():
    table = MagicMock()
    table.get_item.return_value = {}
    repo = ListsRepository(table=table)
    assert repo.get_list("missing") is None


def test_update_list_sets_status_only():
    table = MagicMock()
    repo = ListsRepository(table=table)
    repo.update_list(9, status=STATUS_PROCESSING)
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["Key"] == {"list_id": "9"}
    assert kwargs["UpdateExpression"] == "SET #status = :status"
    assert kwargs["ExpressionAttributeValues"] == {":status": STATUS_PROCESSING}
    assert kwargs["ExpressionAttributeNames"] == {"#status": "status"}


def test_update_list_persists_report_stats():
    table = MagicMock()
    repo = ListsRepository(table=table)
    repo.update_list(
        9,
        report_url="https://drive.example/report",
        num_lines=10,
        num_errors=2,
        error_ratio=0.2,
    )
    kwargs = table.update_item.call_args.kwargs
    values = kwargs["ExpressionAttributeValues"]
    assert values[":report_url"] == "https://drive.example/report"
    assert values[":num_lines"] == 10
    assert values[":num_errors"] == 2
    assert float(values[":error_ratio"]) == 0.2
    assert ":status" not in values
    assert ":finished_at" not in values


def test_update_list_terminal_status_sets_finished_at():
    table = MagicMock()
    repo = ListsRepository(table=table)
    repo.update_list(3, status=STATUS_PROCESSED)
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["Key"] == {"list_id": "3"}
    assert kwargs["ExpressionAttributeValues"][":status"] == STATUS_PROCESSED
    assert kwargs["ExpressionAttributeValues"][":finished_at"]
    assert "finished_at = :finished_at" in kwargs["UpdateExpression"]


def test_update_list_failed_status_sets_finished_at():
    table = MagicMock()
    repo = ListsRepository(table=table)
    repo.update_list(3, status=STATUS_FAILED)
    values = table.update_item.call_args.kwargs["ExpressionAttributeValues"]
    assert values[":status"] == STATUS_FAILED
    assert values[":finished_at"]


def test_update_list_requires_at_least_one_field():
    repo = ListsRepository(table=MagicMock())
    with pytest.raises(ValueError, match="at least one field"):
        repo.update_list(1)
