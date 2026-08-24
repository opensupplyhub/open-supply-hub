"""Unit tests for the ContriBot Monday GraphQL client."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from urllib.error import URLError

import pytest

CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
if str(CONTRIBOT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTRIBOT_DIR))

from lib.monday import MondayBoard  # noqa: E402

COLUMNS = [
    {"id": "name_col", "title": "Contributor Name", "type": "text"},
    {"id": "id_col", "title": "Contributor ID", "type": "text"},
    {"id": "processed_col", "title": "Processed Data", "type": "link"},
    {"id": "hub_col", "title": "OS Hub List Link", "type": "link"},
    {"id": "size_col", "title": "List Size", "type": "numbers"},
]


def _fake_urlopen(responses):
    captured = []

    class FakeResponse:
        def __init__(self, body):
            self._body = body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return self._body

    def fake_urlopen(request, timeout):
        captured.append(request)
        body = responses[len(captured) - 1]
        return FakeResponse(body)

    return captured, fake_urlopen


def test_raises_when_board_id_missing(monkeypatch):
    monkeypatch.delenv("MONDAY_BOARD_ID", raising=False)
    with pytest.raises(RuntimeError, match="MONDAY_BOARD_ID is not configured"):
        MondayBoard(api_url="https://api.monday.com/v2", token="tok")


def test_loads_token_from_secrets_manager(monkeypatch):
    monkeypatch.setenv("MONDAY_API_URL", "https://api.monday.com/v2")
    monkeypatch.setenv("MONDAY_BOARD_ID", "3514246658")
    monkeypatch.setenv(
        "MONDAY_API_KEY_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:monday",
    )
    client = MagicMock()
    client.get_secret_value.return_value = {"SecretString": " monday-token \n"}

    board = MondayBoard(secrets_client=client)

    assert board._token == "monday-token"
    client.get_secret_value.assert_called_once_with(
        SecretId="arn:aws:secretsmanager:us-east-1:123:secret:monday"
    )


def test_create_item_maps_titles_and_posts_column_values(monkeypatch):
    captured, fake_urlopen = _fake_urlopen(
        [
            json.dumps({"data": {"boards": [{"columns": COLUMNS}]}}).encode(),
            json.dumps({"data": {"create_item": {"id": "99"}}}).encode(),
        ]
    )
    monkeypatch.setattr("lib.monday.urlopen", fake_urlopen)

    board = MondayBoard(
        api_url="https://api.monday.com/v2",
        board_id="3514246658",
        token="tok",
    )
    item_id = board.create_item(
        item_name="Spring Facilities",
        contributor_name="Example Brand",
        contributor_id="5",
        processed_url="https://drive.example/report",
        os_hub_url="https://example.com/lists/101",
        list_size=200,
    )

    assert item_id == "99"
    assert len(captured) == 2
    create_body = json.loads(captured[1].data.decode("utf-8"))
    assert "create_item" in create_body["query"]
    variables = create_body["variables"]
    assert variables["boardId"] == "3514246658"
    assert variables["itemName"] == "Spring Facilities"
    values = json.loads(variables["columnValues"])
    assert values["name_col"] == "Example Brand"
    assert values["id_col"] == "5"
    assert values["processed_col"] == {
        "url": "https://drive.example/report",
        "text": "https://drive.example/report",
    }
    assert values["hub_col"] == {
        "url": "https://example.com/lists/101",
        "text": "https://example.com/lists/101",
    }
    assert values["size_col"] == "200"


def test_create_item_wraps_graphql_errors(monkeypatch):
    _captured, fake_urlopen = _fake_urlopen(
        [
            json.dumps({"data": {"boards": [{"columns": COLUMNS}]}}).encode(),
            json.dumps({"errors": [{"message": "boom"}]}).encode(),
        ]
    )
    monkeypatch.setattr("lib.monday.urlopen", fake_urlopen)

    board = MondayBoard(
        api_url="https://api.monday.com/v2",
        board_id="1",
        token="tok",
    )
    with pytest.raises(RuntimeError, match="Monday GraphQL errors"):
        board.create_item(item_name="List")


def test_create_item_wraps_url_errors(monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError("connection refused")

    monkeypatch.setattr("lib.monday.urlopen", fake_urlopen)

    board = MondayBoard(
        api_url="https://api.monday.com/v2",
        board_id="1",
        token="tok",
    )
    with pytest.raises(RuntimeError, match="Monday API request failed"):
        board.create_item(item_name="List")
