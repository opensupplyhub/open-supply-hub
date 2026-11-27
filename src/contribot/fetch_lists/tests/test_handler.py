"""Unit tests for the ContriBot ``fetch_lists`` handler."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Allow ``import handler`` and ``from lib...`` imports when tests run locally.
CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
FETCH_LISTS_DIR = CONTRIBOT_DIR / "fetch_lists"
for path in (str(CONTRIBOT_DIR), str(FETCH_LISTS_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import handler  # noqa: E402

PRESIGNED_FILE_URL = (
    "https://example-files-bucket.s3.eu-west-1.amazonaws.com/"
    "Summer_2026_Suppliers_xYz1234.csv?AWSAccessKeyId=TEST&Signature=abc"
)
PARSED_FILE_KEY = "Summer_2026_Suppliers_xYz1234.csv"


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("CONTRIBOT_STATE_TABLE_NAME", "contribot-state")
    monkeypatch.setenv("OS_HUB_API_URL", "https://example.com")
    monkeypatch.setenv(
        "OS_HUB_API_TOKEN_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:token",
    )


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_empty_table_queries_id_gt_zero(mock_repo_cls, mock_api_cls, env):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 0
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = []

    result = handler.handler({}, None)

    assert result == {"lists": []}
    mock_api_cls.assert_called_once_with()
    api.fetch_lists.assert_called_once_with(
        params={"id__gt": 0, "ordering": "id", "status": "PENDING"},
    )
    repo.advance_cursor.assert_not_called()
    repo.put_list.assert_not_called()


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_uses_cursor_and_enqueues(mock_repo_cls, mock_api_cls, env):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 100
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [
        {
            "id": 101,
            "name": "One",
            "contributor_id": 5,
            "contributor_name": "Contributor One",
            "contributor_email": "one@example.com",
        },
        {
            "id": 102,
            "name": "Two",
            "contributor_id": 6,
            "contributor_name": "Contributor Two",
            "contributor_email": "two@example.com",
            "file": PRESIGNED_FILE_URL,
        },
    ]

    result = handler.handler({}, None)

    api.fetch_lists.assert_called_once_with(
        params={"id__gt": 100, "ordering": "id", "status": "PENDING"},
    )
    assert result == {
        "lists": [{"list_id": "101"}, {"list_id": "102"}],
    }
    assert repo.put_list.call_count == 2
    assert repo.put_list.call_args_list[0].kwargs["file_name"] == ""
    assert repo.put_list.call_args_list[1].kwargs["file_name"] == PARSED_FILE_KEY
    repo.advance_cursor.assert_called_once_with(102)


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_enqueues_before_advancing_cursor(mock_repo_cls, mock_api_cls, env):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 5
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    facility_list = {
        "id": 6,
        "name": "New",
        "contributor_id": 1,
        "contributor_name": "Acme Corp",
        "contributor_email": "admin@acme.com",
        "file": PRESIGNED_FILE_URL,
    }
    api.fetch_lists.return_value = [facility_list]
    order = []

    def track_put(list_id, **kwargs):
        order.append("put")
        return True

    def track_advance(list_id):
        order.append("advance")

    repo.put_list.side_effect = track_put
    repo.advance_cursor.side_effect = track_advance

    result = handler.handler({}, None)

    order.append("return")
    assert order == ["put", "advance", "return"]
    repo.put_list.assert_called_once_with(
        6,
        list_name="New",
        contributor_id=1,
        contributor_name="Acme Corp",
        contributor_email="admin@acme.com",
        file_name=PARSED_FILE_KEY,
    )
    repo.advance_cursor.assert_called_once_with(6)
    assert result == {"lists": [{"list_id": "6"}]}


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_skips_duplicate_list_in_response(mock_repo_cls, mock_api_cls, env):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 5
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [
        {"id": 6, "name": "New", "contributor_id": 1},
        {"id": 7, "name": "Dup", "contributor_id": 2},
    ]
    repo.put_list.side_effect = [True, False]

    result = handler.handler({}, None)

    assert result == {"lists": [{"list_id": "6"}]}
    assert repo.put_list.call_count == 2
    assert repo.put_list.call_args_list[0].kwargs["file_name"] == ""
    assert repo.put_list.call_args_list[1].kwargs["file_name"] == ""
    repo.advance_cursor.assert_called_once_with(7)


# -- OSDEV-3398: wait out the contributor's list-cleaning review window ----


def _list(list_id, minutes_ago):
    from datetime import datetime, timedelta, timezone

    created = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return {
        "id": list_id,
        "name": f"List {list_id}",
        "contributor_id": 1,
        "contributor_name": "Acme",
        "contributor_email": "a@example.com",
        "file": PRESIGNED_FILE_URL,
        "created_at": created.isoformat().replace("+00:00", "Z"),
    }


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_stops_at_the_first_list_younger_than_the_window(
    mock_repo_cls, mock_api_cls, env
):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 10
    repo.put_list.return_value = True
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [
        _list(11, minutes_ago=200),
        _list(12, minutes_ago=95),
        _list(13, minutes_ago=30),  # still under review
        _list(14, minutes_ago=400),  # a later id is never older; left too
    ]

    result = handler.handler({}, None)

    assert result == {"lists": [{"list_id": "11"}, {"list_id": "12"}]}
    assert [c.args[0] for c in repo.put_list.call_args_list] == [11, 12]
    repo.advance_cursor.assert_called_once_with(12)


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_leaves_the_cursor_when_every_list_is_young(
    mock_repo_cls, mock_api_cls, env
):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 10
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [_list(11, minutes_ago=5)]

    result = handler.handler({}, None)

    assert result == {"lists": []}
    repo.put_list.assert_not_called()
    repo.advance_cursor.assert_not_called()


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_processes_lists_without_an_upload_time(
    mock_repo_cls, mock_api_cls, env
):
    repo = MagicMock()
    repo.get_last_list_id.return_value = 10
    repo.put_list.return_value = True
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [
        {"id": 11, "name": "No time", "contributor_id": 1},
        {"id": 12, "name": "Bad time", "contributor_id": 1, "created_at": "soon"},
    ]

    result = handler.handler({}, None)

    assert result == {"lists": [{"list_id": "11"}, {"list_id": "12"}]}
    repo.advance_cursor.assert_called_once_with(12)


@patch("handler.OSHubAPI")
@patch("handler.ListsRepository")
def test_handler_window_is_configurable(mock_repo_cls, mock_api_cls, env, monkeypatch):
    monkeypatch.setenv("CONTRIBOT_MIN_LIST_AGE_MINUTES", "0")
    repo = MagicMock()
    repo.get_last_list_id.return_value = 10
    repo.put_list.return_value = True
    mock_repo_cls.return_value = repo
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_lists.return_value = [_list(11, minutes_ago=1)]

    result = handler.handler({}, None)

    assert result == {"lists": [{"list_id": "11"}]}


def test_min_list_age_defaults_to_ninety_minutes(monkeypatch):
    from datetime import timedelta

    monkeypatch.delenv("CONTRIBOT_MIN_LIST_AGE_MINUTES", raising=False)
    assert handler.min_list_age() == timedelta(minutes=90)
    monkeypatch.setenv("CONTRIBOT_MIN_LIST_AGE_MINUTES", " 120 ")
    assert handler.min_list_age() == timedelta(minutes=120)


def test_created_at_accepts_offsets_and_naive_times():
    from datetime import timezone

    parsed = handler.created_at({"created_at": "2026-11-16T10:00:00.123456Z"})
    assert parsed is not None and parsed.tzinfo is not None
    offset = parsed.utcoffset()
    assert offset is not None and offset.total_seconds() == 0
    naive = handler.created_at({"created_at": "2026-11-16T10:00:00"})
    assert naive is not None
    assert naive.tzinfo == timezone.utc
    assert handler.created_at({}) is None
