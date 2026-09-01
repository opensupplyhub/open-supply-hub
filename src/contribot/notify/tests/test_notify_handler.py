"""Unit tests for the ContriBot ``notify`` handler."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Allow ``from lib...`` and ``from message import`` when tests run locally.
NOTIFY_DIR = Path(__file__).resolve().parents[1]
CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
for path in (NOTIFY_DIR, CONTRIBOT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lib.lists_repository import STATUS_FAILED, STATUS_PROCESSED  # noqa: E402
from message import NotifyMessage  # noqa: E402

# Load the notify handler under a unique module name so it never collides
# with the ``fetch_lists`` handler when both suites run in one session.
_SPEC = importlib.util.spec_from_file_location(
    "notify_handler", CONTRIBOT_DIR / "notify" / "handler.py"
)
handler = importlib.util.module_from_spec(_SPEC)
sys.modules["notify_handler"] = handler
_SPEC.loader.exec_module(handler)


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("CONTRIBOT_STATE_TABLE_NAME", "contribot-state")
    monkeypatch.setenv("ENVIRONMENT", "Test")
    monkeypatch.setenv("OS_HUB_API_URL", "https://example.com")
    monkeypatch.setenv("MONDAY_BOARD_ID", "3514246658")
    monkeypatch.setenv(
        "SLACK_API_URL_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack",
    )
    monkeypatch.setenv(
        "SLACK_FAILURES_API_URL_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack-failures",
    )


LIST_ITEM = {
    "list_id": "101",
    "list_name": "Spring Facilities",
    "contributor_id": "5",
    "contributor_name": "Example Brand",
    "contributor_email": "brand@example.com",
    "file_name": "spring.xlsx",
}


def _mocks(list_item=LIST_ITEM):
    repo = MagicMock()
    repo.get_list.return_value = dict(list_item) if list_item else None
    slack = MagicMock()
    monday = MagicMock()
    return repo, slack, monday


@pytest.fixture
def repo_slack_monday(env):
    repo, slack, monday = _mocks()
    with patch.object(handler, "ListsRepository", return_value=repo), patch.object(
        handler, "SlackWebhook", return_value=slack
    ) as slack_cls, patch.object(
        handler, "MondayBoard", return_value=monday
    ) as monday_cls:
        slack.cls = slack_cls
        monday.cls = monday_cls
        yield repo, slack, monday


def test_handler_posts_success_message(repo_slack_monday):
    repo, slack, monday = repo_slack_monday

    result = handler.handler({"list_id": "101", "status": "processed"}, None)

    assert result == {"list_id": "101", "notified": True}
    slack.cls.assert_called_once_with(
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:slack"
    )
    message = slack.post.call_args[0][0]
    assert message.startswith(
        "[TEST] New list <https://example.com/lists/101|#101 Spring Facilities>"
    )
    assert (
        "<https://example.com/admin/api/contributor/5/change/"
        "|Contributor Example Brand> email brand@example.com" in message
    )
    assert "File spring.xlsx" in message
    assert ":rotating_light:" not in message
    monday.create_item.assert_called_once_with(
        item_name="Spring Facilities",
        contributor_name="Example Brand",
        contributor_id="5",
        processed_url=None,
        os_hub_url="https://example.com/lists/101",
        list_size=None,
    )
    repo.update_list.assert_called_once_with("101", status=STATUS_PROCESSED)


def test_handler_skips_monday_on_failure(repo_slack_monday):
    repo, slack, monday = repo_slack_monday

    event = {
        "list_id": "101",
        "error": {"Error": "States.TaskFailed", "Cause": "boom"},
    }
    result = handler.handler(event, None)

    assert result == {"list_id": "101", "notified": True}
    slack.cls.assert_called_once_with(
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:slack-failures"
    )
    message = slack.post.call_args[0][0]
    assert message.startswith(
        "[TEST] :rotating_light: ContriBot failed to process list"
    )
    assert "Error: boom" in message
    monday.create_item.assert_not_called()
    monday.cls.assert_not_called()
    repo.update_list.assert_called_once_with("101", status=STATUS_FAILED)


def test_handler_requires_monday_board_id(repo_slack_monday, monkeypatch):
    repo, slack, monday = repo_slack_monday
    monkeypatch.delenv("MONDAY_BOARD_ID")

    with pytest.raises(RuntimeError, match="MONDAY_BOARD_ID is not configured"):
        handler.handler({"list_id": "101"}, None)

    slack.post.assert_not_called()
    monday.cls.assert_not_called()
    repo.update_list.assert_not_called()


def test_handler_reraises_monday_failure(repo_slack_monday):
    repo, slack, monday = repo_slack_monday
    monday.create_item.side_effect = RuntimeError("Monday GraphQL errors")

    with pytest.raises(RuntimeError, match="Monday GraphQL errors"):
        handler.handler({"list_id": "101"}, None)

    repo.update_list.assert_not_called()


def test_handler_includes_report_stats_when_present(repo_slack_monday):
    repo, slack, monday = repo_slack_monday

    event = {
        "list_id": "101",
        "num_lines": 200,
        "num_errors": 20,
        "error_ratio": 0.1,
        "report_url": "https://docs.google.com/spreadsheets/d/abc",
    }
    handler.handler(event, None)

    message = slack.post.call_args[0][0]
    assert "<https://docs.google.com/spreadsheets/d/abc|Checked report>" in message
    assert "(200/20) Error ratio: 10.0% :confused:" in message
    monday.create_item.assert_called_once_with(
        item_name="Spring Facilities",
        contributor_name="Example Brand",
        contributor_id="5",
        processed_url="https://docs.google.com/spreadsheets/d/abc",
        os_hub_url="https://example.com/lists/101",
        list_size=200,
    )


@pytest.mark.parametrize(
    "error_ratio,emoji",
    [
        (0.01, ":simple_smile:"),
        (0.1, ":confused:"),
        (0.5, ":disappointed:"),
    ],
)
def test_error_ratio_emoji_thresholds(error_ratio, emoji):
    message = NotifyMessage(
        list_id="101",
        base_url="https://example.com",
        num_lines=100,
        num_errors=1,
        error_ratio=error_ratio,
    ).generate()
    assert emoji in message


@pytest.mark.parametrize(
    "environment,expected_prefix",
    [
        ("Test", "[TEST] "),
        ("Staging", "[STAGING] "),
        ("Production", ""),
        ("", ""),
    ],
)
def test_environment_prefix(environment, expected_prefix):
    message = NotifyMessage(
        list_id="101",
        base_url="https://example.com",
        environment=environment,
    ).generate()
    assert message.startswith(f"{expected_prefix}New list ")


def test_handler_production_message_has_no_prefix(env, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "Production")
    repo, slack, monday = _mocks()
    with patch.object(handler, "ListsRepository", return_value=repo), patch.object(
        handler, "SlackWebhook", return_value=slack
    ), patch.object(handler, "MondayBoard", return_value=monday):
        handler.handler({"list_id": "101"}, None)

    message = slack.post.call_args[0][0]
    assert message.startswith("New list ")


def test_handler_tolerates_missing_dynamodb_row(env):
    repo, slack, monday = _mocks(list_item=None)
    with patch.object(handler, "ListsRepository", return_value=repo), patch.object(
        handler, "SlackWebhook", return_value=slack
    ), patch.object(handler, "MondayBoard", return_value=monday):
        result = handler.handler({"list_id": "999"}, None)

    assert result == {"list_id": "999", "notified": True}
    message = slack.post.call_args[0][0]
    assert "New list <https://example.com/lists/999|#999>" in message
    monday.create_item.assert_called_once_with(
        item_name="#999",
        contributor_name="",
        contributor_id=None,
        processed_url=None,
        os_hub_url="https://example.com/lists/999",
        list_size=None,
    )
    repo.update_list.assert_called_once_with("999", status=STATUS_PROCESSED)


def test_handler_survives_slack_failure(repo_slack_monday):
    repo, slack, monday = repo_slack_monday
    slack.post.side_effect = RuntimeError("Slack webhook request failed")

    result = handler.handler({"list_id": "101"}, None)

    assert result == {"list_id": "101", "notified": False}
    repo.update_list.assert_called_once_with("101", status=STATUS_PROCESSED)
