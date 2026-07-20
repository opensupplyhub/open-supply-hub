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
        params={"id__gt": 0, "ordering": "id"},
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
            "file_name": "one.csv",
        },
        {
            "id": 102,
            "name": "Two",
            "contributor_id": 6,
            "contributor_name": "Contributor Two",
            "contributor_email": "two@example.com",
            "file_name": "two.csv",
        },
    ]

    result = handler.handler({}, None)

    api.fetch_lists.assert_called_once_with(
        params={"id__gt": 100, "ordering": "id"},
    )
    assert result == {
        "lists": [{"list_id": "101"}, {"list_id": "102"}],
    }
    assert repo.put_list.call_count == 2
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
        "file_name": "facilities.csv",
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
        file_name="facilities.csv",
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
    repo.advance_cursor.assert_called_once_with(7)
